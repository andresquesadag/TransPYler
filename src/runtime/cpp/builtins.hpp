// Copyright (c) 2025 Andres Quesada, David Obando, Randy Aguero

#ifndef BUILTINS_HPP
#define BUILTINS_HPP

#include "DynamicType.hpp"
#include <string>

// Python built-in functions

// print() - Output to console
void print(const DynamicType& value);
void print(const DynamicType& v1, const DynamicType& v2);
void print(const DynamicType& v1, const DynamicType& v2, const DynamicType& v3);

// len() - Get length of sequence
DynamicType len(const DynamicType& value);

// range() - Generate sequence of integers
DynamicType range(int stop);
DynamicType range(int start, int stop);
DynamicType range(int start, int stop, int step);

// Type conversion functions
DynamicType str(const DynamicType& value);
DynamicType int_(const DynamicType& value);  // int_ to avoid C++ keyword
DynamicType float_(const DynamicType& value); // float_ to avoid C++ keyword
DynamicType bool_(const DynamicType& value);  // bool_ to avoid C++ keyword

// Math functions
DynamicType abs(const DynamicType& value);
DynamicType min(const DynamicType& a, const DynamicType& b);
DynamicType max(const DynamicType& a, const DynamicType& b);
DynamicType sum(const DynamicType& iterable);

// Utility functions
DynamicType type(const DynamicType& value);
DynamicType input(const std::string& prompt);
DynamicType input();

#endif // BUILTINS_HPP