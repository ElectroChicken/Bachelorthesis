#external a.
#external b.
#external c.

r0 :- a, not b.
{d;c} :- r0.

r1 :- b.
e :- r1.

r2 :- a, b, c.
f :- r2.

r3.
x :- r3.

r4 :- a.
d :- r4.

r5 :- e.



% :- not r1.

% r1 :- b(X).
% a(X) :- b(X).