% a :- b, c.
% b :- a, d.
% e :- b, c, not d.
% a :- d.

% d :- a.
% e :- b, f.
% f :- c, not a.
% {g;d} :- f.
% f :- e.
% {d;c} :- g.
% {c} :- d.

{d;e} :- a.
g :- d, not e.
f :- e, not d.
h :- g.
h :- f.
{d;e} :- h.
:- l.
s.
t :- not x.

% b(X+1) :- a(X), c, X<10.
% a(X+1) :- b(X), d.
% a(X) :- c, X = 2.
% b(2).

% c.


% a :- b, c.
% b :- a, d.
% a :- e.
% {a;b;c;d;e}.

% b. c.
% a. d.
% a.d.c.
