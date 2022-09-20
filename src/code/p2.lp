b(X+1) :- a(X), c, X < 10.
a(X+1) :- b(X), d.
a(3) :- c.

% % Inputs
a(2). c.
% % b(2). d.