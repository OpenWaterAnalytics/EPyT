---
title: 'EPyT: A Python module for EPANET water distribution simulation libraries'
tags:
  - Python
  - EPANET
  - smart water networks
  - hydraulic/quality analysis
authors:
  - name: --------
    orcid: 0000-0000-0000-0000
    equal-contrib: true
    affiliation: "1, 2" # (Multiple affiliations must be quoted)
  - name: Author Without ORCID
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 2
  - name: Author with no affiliation
    corresponding: true # (This is how to denote the corresponding author)
    affiliation: 3
affiliations:
 - name: ---, ---, KIOS, CY
   index: 1
 - name: Institution Name, Country
   index: 2
 - name: Independent Researcher, Country
   index: 3
date: 13 August 2022
bibliography: paper.bib

# Optional fields if submitting to a AAS journal too, see this blog post:
# https://blog.joss.theoj.org/2018/12/a-new-collaboration-with-aas-publishing
# aas-doi: 10.3847/xxxxx <- update this with the DOI from AAS once you know it.
# aas-journal: Astrophysical Journal <- The name of the AAS journal.
---

# Summary

The EPANET-Python Toolkit (EPyT) is an open-source software, originally developed by the [KIOS Research and Innovation Center of Excellence](https://www.kios.ucy.ac.cy/), University of Cyprus which operates within the Python environment, for providing a programming interface for the latest version of EPANET, a hydraulic and quality modeling software created by the US EPA, with Python, a high-level technical computing software. The goal of the EPANET Python Toolkit is to serve as a common programming framework for research and development in the growing field of smart water networks.

# Statement of need

`EPyT` is a python package....

`EPyT` was designed to be used by EMT users[@eliades2016epanet].

An example of a plotted network \autoref{fig:Net2}.

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.
    
For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Example of a network plot:
![Net2 plot showing Pipes,Tanks and Junctions{fig:Net2}](Net2.png)
\autoref{fig:Net2}

# Acknowledgements



# References