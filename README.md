# markdown2bib

Converts simple markdown-formatted APA bibliographies to [bibtex](https://verbosus.com/bibtex-style-examples.html).

## Synopsis

    markdown2bib.py [-h] [-o OUTPUT] infiles [infiles ...]

## Description

Scrape the world's bibliographies!

Make a text file that has one reference per line in the style of the American Psychological Association.
Currently three types of references are supported: `article`, `book`, and `incollection`.
The journal or book titles need to be in [markdown-style bold](http://daringfireball.net/projects/markdown/syntax), meaning `*Set Within Asterixis*`.
For example, `test_bib.md`:

    Baker, D.J. (2015). The Philosophy of Quantum Field Theory. [Preprint]
    Baker, D. J. (2009). Against field interpretations of quantum field theory. *The British Journal for the Philosophy of Science*, 60(3), 585--609.
    Weinberg, S. (1995). *Quantum Theory of Fields, Vol. 1*. Cambridge University Press.
    Redhead, M.L.G. (1988). A Philosopher Looks at Quantum Field Theory. In H. Brown & R. Harr\'{e} (Eds.), *Philosophical Foundations of Quantum Field Theory* (pp. 9-23). Oxford: Clarendon Press.
    Weinberg, S. (1996). What is quantum field theory, and what did we think it is? *Conceptual foundations of quantum field theory: Proceedings, Symposium and Workshop, Boston, USA, March 1-3, 1996*. http://arxiv.org/abs/hep-th/9702027

## Getting started

All you need is a working installation of python.
Try running on the example test file:

    ./markdown2bib.py test_bib.md

## Options

    -h, --help
        Prints this manual and exits.
        
    -o OUTFILE
        Specifies the output filename (out.bib by default).

## Author

Ryan Reece  <ryan.reece@cern.ch>

## License

Copyleft 2016 Ryan Reece     
License: GPL <http://www.gnu.org/licenses/gpl.html>

## TODOs

-   Test things better.
-   ~~Add "edition" for books.~~
-   ~~Allow incollections to be missing the editor.~~
-   Find a way for bibtex notes to be displayed.
-   Eat a baby.


**Created:** 2016-03-15

