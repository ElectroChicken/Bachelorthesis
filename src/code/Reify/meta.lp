conjuction(B) :- literal_tuple(B), hold(L) : literal_tuple(B, L), L>0; not hold(L) : literal_tuple(B, -L), L>0.

body(normal(B)) :- rule(_, normal(B)), conjuction(B).
%body(sum(B, G)) :- rult(_, sum(B,G)), #sum{ W, L:    hold(L), weighted_literal_tuple(B, L, W), L>0;
%                                                 not hold(L), weighted_literal_tuple(B, -L, W), L>0 } >= G.

hold(A) : atom_tuple(H, A) :- rule(disjunction(H), B), body(B).
{ hold(A) : atom_tuple(H, A) } :- rule(choice(H), B), body(B).

% rule coverage
%coveredR(disjunction(R), normal(B)) :- rule(disjunction(R), normal(B)), body(normal(B)).
coveredR((ID1, ID2)) :- rule(ID1, ID2), body(ID2).

% associate the string representation of an atom with its number
atom_t(S, N) :- output(S, T), literal_tuple(T, N).
% input
hold(A) :- input(S), atom_t(S, A).

% associate the string representation of a rule with its number
head((disjunction(R), ID2), S) :- rule(disjunction(R), ID2), atom_tuple(R, H), atom_t(S, H).
body((ID1, normal(B)), S) :- rule(ID1, normal(B)), literal_tuple(B, A), atom_t(S, A), A > 0.
body((ID1, normal(B)), -S) :- rule(ID1, normal(B)), literal_tuple(B, A), atom_t(S, -A), A < 0.


% count how many covered
num_covered(N) :- N = #count{ 1, ID : coveredR(ID) }.
not_covered(N) :- X = #count{ 1, ID1, ID2 : rule(ID1, ID2) }, num_covered(Y), N = X - Y.
cov(X) :- num_covered(N), not_covered(M), X = (N*100)/(M+N).
%:- not coveredR(1).

#show.
%#show T : output(T, B), conjuction(B).
#show coveredR/1.
#show num_covered/1.
#show not_covered/1.
#show cov/1.
%#show head/2.
%#show head(R, H) : head(R, H), coveredR(R).
%#show head(R, H) : head(R, H), not coveredR(R).
%#show body/2.
%#show body(R, B) : body(R, B), coveredR(R).
%#show body(R, B) : body(R, B), not coveredR(R).
%#show atom_t/2.