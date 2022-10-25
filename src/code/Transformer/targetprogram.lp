a :- b, c.
b :- a, d.
a :- e.

_r0 :- b, c.
_r1 :- a, d.
_r2 :- e.

_d0 :- _r0. % _d0 is definition of a
_d0 :- _r2.
_d1 :- _r1. % _d1 is definition of b

% _l0 :- _d0, _d1. % loop between a and b

% _s0 :- _d0, _d1. % scc { a, b }

%%% according to definition these have to also exist but are not necessary
% -> they probably dont slow down the solving but maybe the transforming?
% _l1 :- _d0.
% _l2 :- _d1.
% -> some sccs/loops cant even be represented as they are not definable!
% _s1 :- c.
% _s2 :- d.
% _s3 :- e.
% _l3 :- c.
% _l4 :- d.
% _l5 :- e.

{a;b;c;d;e}.