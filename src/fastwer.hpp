#ifndef FASTWER_FASTWER_HPP
#define FASTWER_FASTWER_HPP

#include <cstdint>
#include <vector>
#include <string>
#include <sstream>
#include <cmath>
#include <stdexcept>

#define WHITESPACE ' '

namespace fastwer {


    void tokenize(const std::string &str, std::vector<std::string> &tokens, bool char_level = false, char delim = WHITESPACE);

    double round_to_digits(double d, uint8_t digits = 4);

    std::pair<uint32_t, uint32_t> compute(std::string &hypo, std::string &ref, bool char_level = false);

    double score_sent(std::string &hypo, std::string &ref, bool char_level = false);

    double score(std::vector<std::string> &hypo, std::vector<std::string> &ref, bool char_level = false);
}

#endif //FASTWER_FASTWER_HPP
