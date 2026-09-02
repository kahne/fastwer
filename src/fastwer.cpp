#include "fastwer.hpp"

#include <algorithm>


namespace {

size_t utf8_code_point_length(const std::string &str, size_t offset) {
    const auto lead = static_cast<unsigned char>(str[offset]);
    size_t length;

    if (lead <= 0x7f) {
        length = 1;
    } else if (lead >= 0xc2 && lead <= 0xdf) {
        length = 2;
    } else if (lead >= 0xe0 && lead <= 0xef) {
        length = 3;
    } else if (lead >= 0xf0 && lead <= 0xf4) {
        length = 4;
    } else {
        throw std::invalid_argument("input contains invalid UTF-8");
    }

    if (offset + length > str.size()) {
        throw std::invalid_argument("input contains truncated UTF-8");
    }
    for (size_t i = 1; i < length; ++i) {
        const auto byte = static_cast<unsigned char>(str[offset + i]);
        if ((byte & 0xc0) != 0x80) {
            throw std::invalid_argument("input contains invalid UTF-8");
        }
    }

    // Reject overlong encodings, UTF-16 surrogate code points, and values
    // beyond the Unicode range.
    if ((lead == 0xe0 && static_cast<unsigned char>(str[offset + 1]) < 0xa0) ||
        (lead == 0xed && static_cast<unsigned char>(str[offset + 1]) > 0x9f) ||
        (lead == 0xf0 && static_cast<unsigned char>(str[offset + 1]) < 0x90) ||
        (lead == 0xf4 && static_cast<unsigned char>(str[offset + 1]) > 0x8f)) {
        throw std::invalid_argument("input contains invalid UTF-8");
    }

    return length;
}

}  // namespace


void fastwer::tokenize(const std::string &str, std::vector<std::string> &tokens, bool char_level, char delim) {
    if (char_level) {
        // Validate and count in one pass so that malformed input is rejected
        // before any token is appended, and the exact size can be reserved.
        size_t n_code_points = 0;
        for (size_t offset = 0; offset < str.size();) {
            offset += utf8_code_point_length(str, offset);
            n_code_points++;
        }
        tokens.reserve(tokens.size() + n_code_points);
        for (size_t offset = 0; offset < str.size();) {
            const size_t length = utf8_code_point_length(str, offset);
            tokens.push_back(str.substr(offset, length));
            offset += length;
        }
    } else {
        std::stringstream ss(str);
        std::string token;
        while (std::getline(ss, token, delim)) { tokens.push_back(token); }
    }
}

double fastwer::round_to_digits(double d, uint8_t digits) {
    if (digits >= 7) {
        throw std::invalid_argument("digits must be less than 7");
    }
    static double pow10[7] = {1, 10, 100, 1000, 10000, 100000, 1000000};
    return std::round(d * pow10[digits]) / pow10[digits];
}

std::pair<uint32_t, uint32_t> fastwer::compute(std::string &hypo, std::string &ref, bool char_level) {
    std::vector<std::string> hypo_tokens, ref_tokens;
    fastwer::tokenize(hypo, hypo_tokens, char_level);
    fastwer::tokenize(ref, ref_tokens, char_level);

    // Use the shorter sequence as columns for O(min(m,n)) space
    const auto &row_tok = (hypo_tokens.size() >= ref_tokens.size()) ? hypo_tokens : ref_tokens;
    const auto &col_tok = (hypo_tokens.size() >= ref_tokens.size()) ? ref_tokens : hypo_tokens;
    uint32_t rows = row_tok.size() + 1, cols = col_tok.size() + 1;

    std::vector<uint32_t> prev(cols), curr(cols);
    for (uint32_t j = 0; j < cols; j++) { prev[j] = j; }
    for (uint32_t i = 1; i < rows; i++) {
        curr[0] = i;
        for (uint32_t j = 1; j < cols; j++) {
            curr[j] = std::min(prev[j] + 1, curr[j - 1] + 1);
            uint32_t match = prev[j - 1] + (row_tok[i - 1] == col_tok[j - 1] ? 0 : 1);
            curr[j] = std::min(curr[j], match);
        }
        std::swap(prev, curr);
    }
    return std::make_pair(prev[cols - 1], ref_tokens.size());
}

double fastwer::score_sent(std::string &hypo, std::string &ref, bool char_level) {
    std::pair<uint32_t, uint32_t> stats = fastwer::compute(hypo, ref, char_level);
    if (stats.second == 0) {
        throw std::invalid_argument("reference must not be empty");
    }
    return fastwer::round_to_digits(100 * double(stats.first) / stats.second, 4);
}

double fastwer::score(std::vector<std::string> &hypo, std::vector<std::string> &ref, bool char_level) {
    size_t n_examples = hypo.size();
    if (n_examples != ref.size()) {
        throw std::invalid_argument("hypo and ref must have the same number of sentences");
    }
    double total_edits = 0.0, total_lengths = 0.0;
    for (size_t i = 0; i < n_examples; i++) {
        std::pair<uint32_t, uint32_t> s = fastwer::compute(hypo[i], ref[i], char_level);
        total_edits += s.first;
        total_lengths += s.second;
    }
    if (total_lengths == 0.0) {
        throw std::invalid_argument("references must not all be empty");
    }
    return fastwer::round_to_digits(100 * total_edits / total_lengths, 4);
}
