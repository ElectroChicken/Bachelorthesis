%#external a.
%#external b.
%#external c.

d :- a, not b.
e :- b.
f :- a, c.
d :- a.
%#show d/0.