#ifndef FASTWER_FASTWER_HPP
#define FASTWER_FASTWER_HPP

#include <vector>
#include <string>
#include <sstream>
#include <cmath>
#include <cassert>

#define WHITESPACE ' '

using namespace std;

namespace fastwer {


    void tokenize(const string &str, vector<string> &tokens, bool char_level = false, char delim = WHITESPACE);

    double round_to_digits(double d, uint8_t digits = 4);

    pair<uint32_t, uint32_t> compute(string &hypo, string &ref, bool char_level = false);

    double score_sent(string &hypo, string &ref, bool char_level = false);

    double score(vector<string> &hypo, vector<string> &ref, bool char_level = false);
}

#endif //FASTWER_FASTWER_HPP
