# Quine-McCluskey Calculator

Takes in a list of minterms and don't cares and returns the minimized sum of product (SOP) and product of sum (POS) forms. Uses the Quine-McCluskey method.

```
usage: qmcalc.py [-h] [-i] [-t TEXT] [-f FILE] [--verbose] [-q]

Calculates the minimum sum-of-products and product-of-sums forms using Quine-McCluskey method for
minterms and don't cares. Written by Michael Riegert in Spring 2021. Tufts University EE26.

optional arguments:
  -h, --help            show this help message and exit
  -i, --interactive     boot into interactive mode (default)
  -t TEXT, --text TEXT  single logic equation to minimize, wrapped in quotes
  -f FILE, --file FILE  read logic equations from file to minimize, equations seperated by newlines
  --verbose             verbose output
  -q, --quiet           only output resulting equation
```

## Equation formatting

Equations are formatted as `m(...)+d(...)` where all numbers in `m(...)` (separated by commas) are the minterms, and all the numbers in `d(...)` (separated by commas) are the don't cares. There can be spaces between any of the numbers or equations and it will still work. There can also be multiple `m` and `d`, and they can be in any order.

All of these are valid inputs representing the same equation:
- `m(0,1,2,3)+d(4,5)`
- `d(4,5)+m(0,1,2,3)`
- `m(0,1)+d(4,5)+m(2,3)`
- `m(0)+m(1)+d(4)+d(5)+m(2)+m(3)`
- ` m ( 0 ) + m ( 1 ) + d ( 4 ) + d ( 5 ) + m ( 2 ) + m ( 3 ) `

## Read from file

By passing in a file using `-f FILENAME`, qmcalc will open the file and read each line as an input equation.

```
$ ./qmcalc.py -f test.txt
read from file

: d( 2, 4) + m( 1, 5, 3)
= A'C + B'C
= (C)(A' + B')

: m(1,2,3,9,10)+d(5,7)
= B'C'D + B'CD' + A'D
= (C + D)(B')(A' + C' + D')

: m(0,2,3,5,6,7,8,10,11,14,15)
= B'D' + C + A'BD
= (B + C + D')(B' + C + D)(A' + C + D')

: m(1,5,3)+d(2,4)
= A'C + B'C
= (C)(A' + B')
```

## Inline text

A single equation can be passed in via calling the command using `-t "EQUATION_TO_SOLVE"`.

```
$ ./qmcalc.py -t "m(1,5,3)+d(2,4)"
inline text

: m(1,5,3)+d(2,4)
= A'C + B'C
= (C)(A' + B')
```

## Interactive prompt

An interactive prompt can be opened for entering equations by passing in `-i`. This is also the default option when called without any command options.

```
$ ./qmcalc.py
interactive prompt

: m(1,2)
= A'B + AB'
= (A + B)(A' + B')

: d(0)
Minterms required

: m(1)+d(2)
= A'B
= (B)(A')

: h
type in a logical equation made of minterms and
dont cares to minimize it
an example is: m(1,2,3,4)+d(6,7)
type q, quit, or exit to exit
type v or verbose to toggle verbose output

:
```
