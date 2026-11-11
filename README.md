# Task 3 — Case Study-Based Analysis and Design using CFG and PDA

**Course:** 21CSC301T — Formal Language and Automata  
**Task:** CLA-2, Task 3  
**Student:** G Tarun Varma  
**Register Number:** RA2411026050037

---

## 1. Project overview

This project presents three case studies that demonstrate how Context-Free Grammars (CFGs) and Pushdown Automata (PDAs) model languages with nested or matching structures.

1. **Balanced bracket validation** — checks correctly nested `()`, `[]`, and `{}`.
2. **Arithmetic-expression syntax** — validates expressions containing `id`, `+`, `*`, and parentheses, with multiplication precedence.
3. **Palindrome recognition** — studies strings over `{a,b}` that read the same forwards and backwards.

Each case study defines its target language, gives a grammar and/or PDA construction, explains derivations or stack behaviour, discusses ambiguity or determinism, and lists accepted and rejected examples.

A finite automaton has only finite control and cannot retain an unbounded nesting history. A PDA adds a last-in-first-out stack, which is suitable for nested delimiters and matching symbols. For arithmetic expressions, parentheses can nest without a fixed depth, and a stack-based parser checks that structure.

## 2. Requirements

- Python 3.9 or later
- No third-party runtime dependencies
- `pytest` is needed only to run the test suite

## 3. Project structure

```text
FLA-Task3-PDA-CFG-Case-Studies/
├── pda_cfg/
│   ├── __init__.py
│   ├── models.py
│   └── cli.py
├── tests/
│   └── test_models.py
├── __init__.py
└── README.md
```

## 4. Installation and execution

Clone the repository and enter its directory:

```bash
git clone https://github.com/gt-varma/FLA-Task3-PDA-CFG-Case-Studies.git
cd FLA-Task3-PDA-CFG-Case-Studies
```

Run all demonstrations:

```bash
python -m pda_cfg.cli all
```

Run an individual case study:

```bash
python -m pda_cfg.cli brackets
python -m pda_cfg.cli expression
python -m pda_cfg.cli palindrome
```

Run the tests:

```bash
python -m pip install pytest
python -m pytest tests -q
```

## 5. Case study 1 — Balanced bracket validation

### 5.1 Target language

Let \(\Sigma = \{(,),[,],\{,\}\}\). The language \(L\) contains all **non-empty** strings over this alphabet in which every closing bracket matches the most recent unmatched opening bracket and no opening bracket remains unmatched at the end.

**Accepted examples:** `()`, `[]{}`, `([]{})`, `{[()()]}`, `(((())))`.

**Rejected examples:** `(`, `)(`, `([)]`, `(()`, `{]}`.

### 5.2 Context-Free Grammar

A compact grammar is:

```text
S → SS | (S) | [S] | {S} | () | [] | {}
```

The `SS` alternative permits concatenation of multiple balanced blocks. However, this grammar is ambiguous because a concatenated string can be grouped in more than one way.

For `()()()`, two distinct derivation paths are possible:

```text
S ⇒ SS ⇒ (SS)S ⇒ ()SS ⇒ ()()S ⇒ ()()()
S ⇒ SS ⇒ S(SS) ⇒ ()(SS) ⇒ ()()S ⇒ ()()()
```

These correspond to the two parse-tree groupings `(SS)S` and `S(SS)`.

An unambiguous revised grammar is:

```text
S → B S | B
B → (S) | () | [S] | [] | {S} | {}
```

Here, `S` is a non-empty sequence of blocks and `B` is exactly one bracketed block. The right-recursive sequence fixes the grouping of concatenation.

### 5.3 PDA construction

Define the deterministic PDA as \(M=(Q,\Sigma,\Gamma,\delta,q_0,Z_0,F)\):

- States: \(Q=\{q_0,q_1,q_f\}\). \(q_0\) is the start state and \(q_f\) is the accepting state.
- Input alphabet: \(\Sigma=\{(,),[,],\{,\}\}\).
- Stack alphabet: \(\Gamma=\{Z_0,(,[,\{\}\}\), where \(Z_0\) is the bottom-of-stack marker.
- Final states: \(F=\{q_f\}\).
- Acceptance: all input is consumed and the machine reaches \(q_f\) with only \(Z_0\) remaining.

For each opening bracket \(o\) and stack top \(X\), the machine pushes the opener:

- \(\delta(q_0,o,Z_0)=(q_1,oZ_0)\)
- \(\delta(q_1,o,X)=(q_1,oX)\)

For each matching opener/closer pair \((o,c)\), it pops the opener:

- \(\delta(q_1,c,o)=(q_1,\varepsilon)\)

When input is exhausted and the stack top is \(Z_0\):

- \(\delta(q_1,\varepsilon,Z_0)=(q_f,Z_0)\)

No transition is defined for a mismatched closer, an unexpected symbol, or a non-empty stack at end of input. The transition notation writes the new stack string with its leftmost symbol on top.

### 5.4 Successful stack processing

For `{[()]}`, the top of the stack is shown at the left:

```text
(q0, {[()]}, Z0)
⊢ (q1, [()]}, { Z0)
⊢ (q1, ()]}, [ { Z0)
⊢ (q1, )]}, ( [ { Z0)
⊢ (q1, ]}, [ { Z0)
⊢ (q1, }, { Z0)
⊢ (q1, ε, Z0)
⊢ (qf, ε, Z0)  ACCEPT
```

For `([)]`, after reading `([ ` the stack top is `[`. The next input is `)`, for which no matching-pop transition exists. The machine rejects.

### 5.5 Implementation

The function `balanced_brackets(text)` in `pda_cfg/models.py` uses a stack:

1. Push every opening bracket.
2. For a closing bracket, check that the stack is non-empty and its top is the matching opener.
3. Reject immediately for a mismatch or an unsupported character.
4. Accept only if the input is non-empty and the stack is empty at the end.

**Limitation:** this model validates delimiter nesting only. It does not check programming-language types, statement syntax, or whether delimiters occur inside comments or string literals. A practical source-code validator would first need lexical analysis.

## 6. Case study 2 — Arithmetic-expression syntax

### 6.1 Target language

The token alphabet is \(\Sigma=\{id,+,*,(,)\}\). The language contains expressions built from the identifier token `id`, binary addition and multiplication, and parentheses.

- Unary operators and implicit multiplication are excluded.
- Multiplication has higher precedence than addition.
- Both operators are left-associative.

**Accepted examples:** `id`, `id+id*id`, `(id+id)*id`, `id*(id+id)`, `((id))`.

**Rejected examples:** empty input, `id+`, `+id`, `id id`, `(id+id`, `id+*id`.

### 6.2 Ambiguous grammar

A naïve grammar is:

```text
E → E + E | E * E | (E) | id
```

For `id + id * id`, two structures are possible:

- `id + (id * id)`
- `(id + id) * id`

The grammar does not encode precedence and is ambiguous.

### 6.3 Grammar with precedence

The following grammar gives multiplication higher precedence than addition:

```text
E → E + T | T
T → T * F | F
F → (E) | id
```

- `E` handles addition.
- `T` handles multiplication.
- `F` handles identifiers or parenthesised expressions.

For predictive parsing, remove left recursion:

```text
E  → T E'
E' → + T E' | ε
T  → F T'
T' → * F T' | ε
F  → ( E ) | id
```

This grammar supports a deterministic LL(1) predictive parser.

### 6.4 PDA construction

The standard CFG-to-NPDA construction uses one state \(q\) and a stack initially containing the start variable \(E\):

1. For each production \(A\to\alpha\), add an epsilon transition that replaces \(A\) on the stack with \(\alpha\).
2. For each terminal \(a\), add a transition that reads \(a\) from the input and pops the matching terminal \(a\) from the stack.
3. Accept when the input is consumed and the stack is empty.

This generic construction is nondeterministic because it chooses among productions using epsilon moves.

The executable parser uses the left-recursion-free grammar and one look-ahead token. Its parser procedures correspond to \(E,E',T,T',F\). It is a deterministic predictive parser rather than the generic NPDA above.

### 6.5 Leftmost derivation

For `id + id * id`:

```text
E
⇒ E + T
⇒ T + T
⇒ F + T
⇒ id + T
⇒ id + T * F
⇒ id + F * F
⇒ id + id * F
⇒ id + id * id
```

The multiplication is contained within \(T\), showing that it binds more tightly than addition.

### 6.6 Implementation and validation

The function `validate_expression(source)` tokenises the input and invokes the predictive parser. The parser returns an acceptance result, a message, and a trace of matched tokens or the rejection reason.

The tokenizer recognises the identifier token `id`, whitespace, and the symbols `+`, `*`, `(`, and `)`. Unsupported characters or tokens are rejected.

**Limitation:** this is a syntax model over abstract tokens, not a complete programming language. It does not evaluate values, detect division by zero, resolve variable names, or enforce types. A real compiler also performs lexical, semantic, and type analysis.

## 7. Case study 3 — Palindrome recognition

### 7.1 Target language

Let \(\Sigma=\{a,b\}\). Define:

\[
L_{pal}=\{w\in\Sigma^*:w=w^R\}
\]

where \(w^R\) is the reverse of \(w\). The empty string \(\varepsilon\) is included. This language contains both odd- and even-length palindromes.

**Accepted examples:** \(\varepsilon\), `a`, `aba`, `abba`, `babab`, `aabaa`.

**Rejected examples:** `ab`, `aab`, `abab`, `abbab`, `ba`.

### 7.2 Context-Free Grammar

```text
S → aSa | bSb | a | b | ε
```

The recursive rules add the same symbol at both ends. The base cases generate the empty string or a one-symbol centre.

Example derivation for `abba`:

```text
S ⇒ aSa
  ⇒ abSba
  ⇒ abεba
  ⇒ abba
```

Example derivation for `aba`:

```text
S ⇒ aSa
  ⇒ aba
```

The grammar is unambiguous: the outermost symbols determine which recursive production applies, and the centre is determined when zero or one symbols remain.

### 7.3 PDA strategy and determinism

For an unmarked palindrome, a PDA must guess the midpoint. An NPDA:

1. Pushes symbols while reading the first half.
2. Nondeterministically takes an epsilon transition to a matching phase.
3. Compares and pops one stack symbol for each remaining input symbol.
4. Accepts when input is exhausted and only the bottom marker remains.

To cover even lengths, it switches phases between input symbols. To cover odd lengths, it may consume exactly one middle symbol during the switch without pushing or popping it. The midpoint guess is the source of nondeterminism.

If the input format contains a special centre marker `c`, the language \(\{wcw^R:w\in\{a,b\}^*\}\) can be recognised deterministically: push symbols before `c`, switch phase when `c` is read, and compare/pop after `c`. The marker makes the midpoint explicit. This marked-centre language is a format variant, not the same input language as all unmarked palindromes.

The CFG above describes all palindromes. The Python function `is_palindrome(text)` checks the defining reversal property as a reference validator; it is **not** presented as a literal PDA simulator. The NPDA/DPDA stack procedures above are the formal automata design.

### 7.4 Implementation and validation

The function `is_palindrome(text)` checks that every character belongs to `{a,b}` and that the string equals its reverse. The function `palindrome_derivation(text)` returns the sequence of grammar-production choices for a valid palindrome, or `None` for an invalid string.

**Limitation:** the checker accepts only the alphabet \(\{a,b\}\). It is a formal-language demonstration, not a secure password checker or a natural-language palindrome tool.

## 8. Comparison of the three case studies

| Case study | Why finite-state memory is insufficient | Stack/grammar feature |
|---|---|---|
| Balanced brackets | Arbitrarily deep nesting and matching types | Deterministic push/pop |
| Arithmetic expressions | Arbitrarily nested parentheses | CFG with precedence; predictive parser |
| Palindromes | Matching an unbounded first half with its reverse | NPDA midpoint guess; DPDA when centre marker is explicit |

The three examples show different uses of context-free modelling: nested structure, precedence-aware syntax, and mirrored strings. Ambiguity is exposed and corrected for bracket concatenation and arithmetic precedence. Determinism depends on the input structure: the bracket PDA is deterministic, the revised expression grammar supports LL(1) parsing, and unmarked palindrome recognition uses nondeterministic midpoint selection.

## 9. How to demonstrate the project

1. Run `python -m pda_cfg.cli all` to display the accepted and rejected examples for all three case studies.
2. Demonstrate the bracket stack on `{[()]}` and explain why `([)]` is rejected.
3. Explain why `id+id*id` parses with multiplication first.
4. Show the CFG derivation of `abba` and explain the guessed midpoint for an unmarked palindrome NPDA.
5. Explain the limitations of each executable validator and distinguish the formal PDA design from the reference palindrome checker.

## 10. Files and implementation details

| File | Purpose |
|---|---|
| `pda_cfg/models.py` | Bracket-stack recognizer, expression predictive parser, palindrome recognizer and derivation helper |
| `pda_cfg/cli.py` | Command-line demonstrations for all three case studies |
| `tests/test_models.py` | Positive and negative validation tests |

---

**Prepared by:** G Tarun Varma  
**Register Number:** RA2411026050037  
**Course:** 21CSC301T — Formal Language and Automata
