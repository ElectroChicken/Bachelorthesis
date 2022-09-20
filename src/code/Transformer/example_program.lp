%%% Complex structures in the head %%%
% Aggregates with left and right guards
1 { y; z } 2 :- x.
% Conditional literals
2 { a(X,Y) : c(Y) } 3 :- b(X).
% Choice rules
{ d } :- z.
% Disjunctions
e ; f :- y.
% Constraints
:- f.
% Variables
a(D) :- b(D).
a(A) :- t(A, _).
a(D, E) :- t(D, E).


%%% Complex structures in the body %%%
% Aggregates with guards
test(X) :- b(X), { a(X,_) } = 2.
% Conditional literals
test2(X) :- b(X), c(Y) : a(X, Y).
% Disjunction
s :- z ; e.

% len(ele[0].literal.atom.symbol.arguments)

% Input
% x, b(X), c(Y), t(X, Y)