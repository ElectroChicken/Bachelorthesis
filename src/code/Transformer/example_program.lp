% Normal rule
b :- x.

% Constraints
:- f.

% Facts
g.

% Choice rules
{ d } :- z.

% Aggregates with left and right guards
1 { y; z } 2 :- x.  % in the head
1 #sum{1,m : m; 3,n : n; -2,o : o} 3 :- d.
p :- 2 { y; z }.    % in the body
c :- #count{1 : y; 2 : z; 3 : b} = 2.   
s :- 2 #sum{1,d : d; 2,y : y; 2,z : z; -3,e : e} 3.
s2 :- 2 #sum+{1,d : d; 2,y : y; 2,z : z; -3,e : e} 3.
min :- #min{1,d : d; 2,y : y; 2,z : z; -3,e : e} = -3.
max :- #max{1,d : d; 2,y : y; 2,z : z; -3,e : e} = 2.

% Disjunctions
e ; f :- y.

% #true/#false (#false in head = constraint)
#true :- e.     % in the head
t :- #true.     % in the body
f :- #false.

% Conditional literals
i : e :- b.     % in the head
j :- y : d.     % in the body

% Arithmetic functions?
h :- y < z.     % in the body
h > a :- g.     % in the head

% Optimization
#minimize{1,d : d; -2,y : y; 2,z : z; -3,e : e; 4,f : f; 1,t : t; 2,i : i; -1,j : j}.
#maximize{1,d : d; -2,y : y; 2,z : z; -3,e : e; 4,f : f; 1,t : t; 2,i : i; -1,j : j}.

% External functions
% #script (python)
% import clingo
% import random
% N=clingo.Number
% def rnd():
%     return N(random.randint(1,4))

% #end.
% r :- @rnd() > 2.

% % #show
#show.
#show d/0.
#show r/0.
#show wow : r, d.

% #external
#external k : e.
d :- k.

% #include
#include "novar.lp".

% #const
#const p = 42.