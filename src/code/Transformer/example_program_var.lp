% Normal rule
b(X) :- a(X).
b(D) :- a(_, D).
a(C, D) :- t(C, D).
% Constraints
:- f(X), X>2.

% Facts
g(2).

% Choice rules
{ d(X) } :- z(X).

% Aggregates with left and right guards
1 { y(X); z(X) } 2 :- a(X).  % in the head
1 #sum{1,m : m(X); 3,n : n(X); -2,o : o(X)} 3 :- d(X).
test(X) :- b(X), { a(X,_) } = 2.                % in the body
c :- #count{1 : y(X); 2 : z(X); 3 : b(X)} = 7.   
s(S) :- S = #sum{X,d : d(X); X,y : y(X); X,z : z(X); X,e : e(X)}.
s2(S) :- S = #sum+{-X,d : d(X); X,y : y(X); X,z : z(X); X,e : e(X)}.
min(M) :- M = #min{X,d : d(X); X,y : y(X); X,z : z(X); X,e : e(X)}.
max(M) :- M = #max{X,d : d(X); X,y : y(X); X,z : z(X); X,e : e(X)}.

% Disjunctions
e(X) ; e(-X) :- g(X).

% #true/#false (#false in head = constraint)
#true :- e(2).
t(1) :- #true.
f(3) :- #false.

% Arithmetic functions / comparisons
f(X) :- min(X), max(Y), X>Y.
sum(X+Y) :- s(X), s2(Y).
m(X) :- z(X*2).

% Intervals
i(X..Y) :- t(X,Y).      
j(X) :- max(M), X=1..M.

% pools
c(X;Y):- a(X,Y).    
% :- c(5;10).         

% Conditional literals
% k(X) : e(-X) :- b(X).           % in the head
2 { a(X,Y) : c(Y) } 3 :- b(X).
x(X) :- b(X), c(Y) : a(X, Y).   % in the body

% Optimization
#minimize{X : min(X)}.
#maximize{X,max : max(X); Y,sum : sum(Y)}.

% Constraint terms, disjoint constraints
#const v=4.
1 $<= $queen(1..v) $<= v.
$queen(X) $!= $queen(Y) :- X=1..v, Y=1..v, X<Y.
#disjoint { X : $queen(X) $+ X : X=1..v }.

% Theory atoms etc
#theory difference {
    constant { - : 0 , unary };
    diff_term { - : 0 , binary, left };
    linear_term { + : 2 , unary ; - : 2 , unary ;
                  * : 1 , binary, left ;
                  + : 0 , binary, left ; - : 0 , binary, left };
    domain_term { .. : 1 , binary, left };
    show_term { / : 1 , binary, left };
    &dom /0 : domain_term, {=} , linear_term, any ;
    &sum /0 : linear_term, { <= , =, >= , <, > , !=} , linear_term, any ;
    &diff /0 : diff_term, { <=} , constant, any ;
    &show /0 : show_term, directive
}.
#const n =2. #const m =1000.
task (1.. n ). duration ( T,200 * T ) :- task ( T ).
&dom { 1.. m } = start ( T ) :- task ( T ).
&dom { 1.. m } = end ( T ) :- task ( T ).
&diff { end ( T ) - start ( T ) } <= D :- duration ( T,D ).
&sum { end ( T ) : task ( T ); - start ( T ) : task ( T ) } <= m .
&show { start /1; end /1 }.

% External functions
% #script (python)
% import clingo
% import random
% N=clingo.Number
% def rnd(x):
%     return N(random.randint(1,x))

% #end.
% r(@rnd(X)) :- a(X).

% % #show
% #show.
% #show sum/1.
% #show r/1.
% #show X : a(X), c(X).
% #show c/1.

% #external
#external h(X) : a(X).
l(X-3) :- h(X), X>3.

% #include
#include "var.lp".

% #const
#const p = 42.
wow :- p = 42.