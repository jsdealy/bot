#include <iostream>
#include <cstdlib>
#include <fstream>
#include "jtb/jtbstr.h"




int main(int argc, char **argv) {
    if (argc <= 1) throw std::runtime_error("not enough clargs");
    std::ifstream file(argv[1]);
    if (file.bad()) { throw std::runtime_error("problem opening file"); }
    JTB::Str strBuffer {};
    char buff[200];
    int count {0};
    while (file.good()) {
	file.getline(buff, 199);
	if (!file.good()) break;
	strBuffer.clear();
	strBuffer.push(buff);
	JTB::Vec<JTB::Str> lineVec {};
	JTB::Vec<JTB::Str> justinVec {};
	JTB::Vec<JTB::Str> timVec {};
	JTB::Vec<JTB::Str> louisVec {};
	JTB::Vec<JTB::Str> patrickVec {};
	if (strBuffer.startsWith('"')) {
	    lineVec.push(strBuffer.substrInBounds('"', '"', JTB::Str::Bounds::INC));
	    lineVec.push(strBuffer.substrInBounds("\",", ",", 1, 1, JTB::Str::Bounds::EXC));
	    justinVec.push(std::to_string(count));
	}
	else {
	    lineVec.push(strBuffer.sliceAtChar(','));
	    lineVec.push(strBuffer.substrInBounds(',', ',', 1, 1, JTB::Str::Bounds::EXC));
	}
	
	std::cout << count++;
	lineVec.forEach([&](JTB::Str s) {
	    std::cout << "," << s;
	});
	std::cout << '\n';
    }
}


