#ifndef FASTWER_FASTWER_HPP
#define FASTWER_FASTWER_HPP

#include <cstdint>
#include <vector>
#include <string>
#include <cmath>
#include <stdexcept>

namespace fastwer {

    constexpr char kWhitespace = ' ';

    void tokenize(const std::string &str, std::vector<std::string> &tokens, bool char_level = false, char delim = kWhitespace);

    double round_to_digits(double d, uint8_t digits = 4);

    std::pair<uint32_t, uint32_t> compute(const std::string &hypo, const std::string &ref, bool char_level = false);

    double score_sent(const std::string &hypo, const std::string &ref, bool char_level = false);

    double score(const std::vector<std::string> &hypo, const std::vector<std::string> &ref, bool char_level = false);
}

#endif //FASTWER_FASTWER_HPP
