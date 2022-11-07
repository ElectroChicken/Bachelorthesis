% p(1). p(2). p(3).
% #external q(X) : p(X).
% q(1).
% r(X) :- q(X).

1 #sum{1,m : m(X); 3,n : n(X); -2,o : o(X)} 3 :- d(X).
{d(X)}:-z(X).
1{y(X);z(X)}2:-a(X).


% #const v=4.
1 $<= $queen(1..v) $<= v.
$queen(X) $!= $queen(Y) :- X=1..v, Y=1..v, X<Y.
#disjoint { X : $queen(X) $+ X : X=1..v }.