"""
A 10-state 1D cellular automaton that implements steps of the Collatz conjecture.
This shows that the step function is full parallelizable, i.e. it can be
performed in O(1) work per step if you have unlimited machines.

There are 3 initial states for cells:
  * 0 and 1  - the binary digits of the input values
  * S = STOP - an empty state for every cell index not 0 or 1

Recall that the Collatz step is

  n ->  n/2     if n is even
    ->  3n+1/2  if n is odd

The division by 2 can be accomplished without shifting digits by
erasing the final digit, i.e. overwriting the final digit with 'S'.

The multiplication by 3 is equivalent to a left-shift and an add.
The trick here is that the shift and the add don't need to happen
for all the digits in the same step. We can go from right to left
performing the shift and add one digit per tick.

We introduce 7 extra states to track the in-progress shift and add
operations:

  (0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (1,3)

If the Collatz conjecture is true, the system ends up back at the
terminal state S1S for all positive inputs.
"""


symbols = ["S", 0, 1, (0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (1,3)]



def collatz_rule(left, c, right):
  """
  Moves the cellular automaton one step forward.
  Each cell's future value depends only on its current value and the
  current value of its neighbors.

  If x_i,t is the value of the i'th cell at time t, given inputs

  left   = x_i-1,t
  c      = x_i,  t
  right  = x_i+1, t

  This returns x_i,t+1.
  """

  # right=S indicates this is the right-most digit
  if right == "S" and c == 0:
    # Division by 2 by erasing the right-most 0 (replacing with 'S').
    return "S"

  elif right == "S" and c == 1:
    # State that will trigger performing a 3x+1 operation on all digits,
    # one digit per tick.
    return (1, 2)

  # If the current state represents a shift/add operation in progress,
  # let's resolve that.
  if c not in ["S", 0, 1]:
    if c[1] % 2 == 1:
      # If our carry state looks like (?,1) or (?,3), this digit becomes a 1.
      return 1

    if right == "S":
      # Optimization: we could just return 0 here, but we may as
      # well do the divide by 2 in the same step.
      return "S"

    # This state is a (?,0) state, and it becomes a zero.
    return 0

  # If the cell to the right has a carry operation in progress.
  elif right not in ["S", 0, 1]:
    x = right[0]
    y = right[1]
    if c == 1:
      z = 1
    else:
      z = 0
    if c == "S" and z == 0 and z + x + (y // 2) == 0:
      return "S"
    else:
      return (z, z + x + (y // 2))

  else:
    return c

def multiply_add_one_rule(left, c, right):
  if right == "S" and c in [0, 1]:
    return c
  elif c not in ["S", 0, 1]:
    return c[1] % 2
  else:
    return collatz_rule(left, c, right)


def mapsymbol(c):
  """Turns a cell state into a human-readable string of length 1."""

  if c == "S":   return "S"
  if c == 0:     return "0"
  if c == 1:     return "1"
  if c == (0,0): return "a"
  if c == (0,1): return "b"
  if c == (0,2): return "c"
  if c == (1,0): return "A"
  if c == (1,1): return "B"
  if c == (1,2): return "C"
  if c == (1,3): return "D"
  raise ValueError("Unexpected {}".format(c))

def reversemap(c):
  for s in symbols:
    if mapsymbol(s) == c: return s
  raise ValueError("Unexpected {}".format(c))


def iterate_rule(s, rule):
  """
  Applies a cellular automaton rule to a list of cell values, returning new cell values
  as a string. The input string should start and end with S.

  S is a special empty state that is conceptually in all cells that don't have a value.
  The return value can be shorter if a left or right cell became S, or longer if an S
  cell become non-S.
  """

  t = []
  for i in range(0, len(s)):
    # When index is out of bounds for left or right, that's "S"
    left = s[i - 1] if i > 0 else "S"
    right = s[i + 1] if i < len(s) - 1 else "S"

    c = s[i]
    t.append(mapsymbol(
        rule(
          reversemap(left),
          reversemap(c),
          reversemap(right))))
  return "S" + "".join(t).strip("S") + "S"


def run(n):
  """
  Given a positive integer, runs its Collatz sequence until it terminates.
  Under the hood, this uses a cellular automaton.

  Return (steps taken, max string length).
  """

  s = "S{0:b}S".format(n)
  steps = 0
  maxlen = 0
  while True:
    print(s.rjust(40))
    maxlen = max(len(s), maxlen)
    if s[:3] == "S1S":
      return (steps, maxlen)
    s = iterate_rule(s, collatz_rule)
    steps += 1

def test_multiply():
  for n in range(3, 100, 2):
    s = "S" + "{0:b}".format(n // 2) + "CS"
    s_old = ""
    while s_old != s:
      s_old = s
      s = iterate_rule(s, multiply_add_one_rule)
    x = int(s[1:-1], 2)
    if x != 3 * n + 1:
      raise ValueError(n)
    # print("{} * 3 + 1 --> {} [{}]".format(n, s, x))

test_multiply()


# TODO: needs more tests to prove that the step function
#       correctly implements the Collatz step.

m = 0
for n in [6171]:
  (steps, maxlen) = run(n)
  if maxlen > m:
    m = maxlen
    print("{} reached a max length of {}".format(n, m))


