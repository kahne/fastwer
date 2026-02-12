#include "fastwer.hpp"


void fastwer::tokenize(const std::string &str, std::vector<std::string> &tokens, bool char_level, char delim) {
    std::stringstream ss(str);
    std::string token;
    if (char_level) {
        for (char c : str) { tokens.push_back(std::string(1, c)); }
    } else {
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

    uint32_t m = hypo_tokens.size() + 1, n = ref_tokens.size() + 1;
    std::vector<uint32_t> f(m * n);
    for (size_t i = 0; i < m; i++) { f[i * n] = i; }
    for (size_t j = 0; j < n; j++) { f[0 * n + j] = j; }
    for (size_t i = 1; i < m; i++) {
        for (size_t j = 1; j < n; j++) {
            f[i * n + j] = std::min(f[(i - 1) * n + j] + 1, f[i * n + (j - 1)] + 1);
            uint32_t matching_case = f[(i - 1) * n + (j - 1)] + (hypo_tokens[i - 1] == ref_tokens[j - 1] ? 0 : 1);
            f[i * n + j] = std::min(f[i * n + j], matching_case);
        }
    }
    return std::make_pair(f[m * n - 1], ref_tokens.size());
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
