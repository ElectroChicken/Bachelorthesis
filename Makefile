build:
	latexmk -pdf -halt-on-error -cd -outdir=../target src/main.tex

show: build
	xdg-open target/main.pdf

clean:
	rm -r target