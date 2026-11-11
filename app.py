import streamlit as st

from pda_cfg.models import (
    OPEN_TO_CLOSE,
    balanced_brackets,
    validate_expression,
    is_palindrome,
    palindrome_derivation,
)

st.set_page_config(
    page_title="FLA Task 3 | CFG & PDA Case Studies",
    page_icon="🔁",
    layout="wide",
)

st.title("Formal Language and Automata — Task 3")
st.caption("Case Study-Based Analysis and Design using Context-Free Grammar and Pushdown Automata")
st.markdown(
    "**Student:** G Tarun Varma  |  **Register No.:** RA2411026050037  |  **Course:** 21CSC301T"
)

st.info(
    "Explore three language-recognition case studies. Enter a string or expression "
    "to see whether the implementation accepts it and inspect the corresponding "
    "stack/parser trace or grammar derivation."
)

tab_brackets, tab_expression, tab_palindrome, tab_theory = st.tabs(
    ["Balanced Brackets", "Arithmetic Expressions", "Palindromes", "CFG & PDA Notes"]
)

with tab_brackets:
    st.subheader("Case Study 1 — Balanced Bracket Validation")
    st.write("Language: non-empty, correctly nested strings over (), [] and {}.")
    bracket_input = st.text_input("Enter a bracket string", value="{[()]}", key="bracket_input")
    if st.button("Validate brackets", key="check_brackets"):
        stack = []
        trace = []
        accepted = bool(bracket_input)
        if not bracket_input:
            trace.append("Reject: the language excludes the empty string.")
        for index, char in enumerate(bracket_input):
            if char in OPEN_TO_CLOSE:
                stack.append(char)
                trace.append(f"Read {char!r}: push; stack = {stack}")
            elif char in OPEN_TO_CLOSE.values():
                if not stack:
                    trace.append(f"Read {char!r}: reject; no opening bracket is available.")
                    accepted = False
                    break
                opener = stack[-1]
                if OPEN_TO_CLOSE[opener] != char:
                    trace.append(
                        f"Read {char!r}: reject; stack top {opener!r} expects "
                        f"{OPEN_TO_CLOSE[opener]!r}."
                    )
                    accepted = False
                    break
                stack.pop()
                trace.append(f"Read {char!r}: matching pop; stack = {stack}")
            else:
                trace.append(f"Reject: unsupported character {char!r}.")
                accepted = False
                break
        if accepted and stack:
            trace.append(f"Reject: unmatched opening brackets remain: {stack}")
            accepted = False
        elif accepted:
            trace.append("Input consumed and stack empty: ACCEPT.")
        if accepted:
            st.success("Accepted — the brackets are balanced.")
        else:
            st.error("Rejected — the string is not in the balanced-bracket language.")
        st.code("\n".join(trace) if trace else "No processing steps.")
    with st.expander("CFG and PDA model"):
        st.markdown("**Ambiguous CFG**")
        st.code("S → SS | (S) | [S] | {S} | () | [] | {}")
        st.markdown("**Unambiguous revised CFG**")
        st.code("S → BS | B\nB → (S) | () | [S] | [] | {S} | {}")
        st.markdown(
            "The deterministic PDA pushes each opening bracket. On a closing bracket, "
            "it pops only the matching opener. It accepts after all input is consumed "
            "and only the bottom-of-stack marker remains."
        )
        st.caption("This implementation exposes the stack operations directly.")

with tab_expression:
    st.subheader("Case Study 2 — Arithmetic Expression Syntax")
    st.write("Tokens: id, +, *, and parentheses. Multiplication has higher precedence than addition.")
    expression_input = st.text_input(
        "Enter an expression", value="id+id*id", key="expression_input"
    )
    if st.button("Parse expression", key="check_expression"):
        result = validate_expression(expression_input)
        if result.accepted:
            st.success("Accepted — the expression is syntactically valid.")
        else:
            st.error(f"Rejected — {result.message}")
        st.markdown("**Predictive parser trace**")
        st.code("\n".join(result.trace))
    with st.expander("CFG and PDA model"):
        st.markdown("**Naïve ambiguous grammar**")
        st.code("E → E + E | E * E | (E) | id")
        st.markdown("**Grammar encoding precedence**")
        st.code("E → E + T | T\nT → T * F | F\nF → (E) | id")
        st.markdown("**Left-recursion-free predictive grammar**")
        st.code("E  → T E'\nE' → + T E' | ε\nT  → F T'\nT' → * F T' | ε\nF  → ( E ) | id")
        st.markdown(
            "A general CFG-to-NPDA construction uses epsilon transitions to expand "
            "variables and input-consuming transitions to match terminals. The executable "
            "implementation is a deterministic predictive parser using look-ahead; "
            "it is not a literal simulation of that generic NPDA."
        )

with tab_palindrome:
    st.subheader("Case Study 3 — Palindrome Recognition")
    st.write("Language: L = { w ∈ {a,b}* : w = reverse(w) }. The empty string is included.")
    palindrome_input = st.text_input(
        "Enter a string using only a and b", value="abba", key="palindrome_input"
    )
    if st.button("Check palindrome", key="check_palindrome"):
        accepted = is_palindrome(palindrome_input)
        if accepted:
            st.success("Accepted — the string is a palindrome.")
            derivation = palindrome_derivation(palindrome_input)
            st.markdown("**CFG production choices**")
            st.code("\n".join(derivation or ()))
        else:
            st.error("Rejected — the string is not a palindrome over {a,b}.")
            if any(char not in "ab" for char in palindrome_input):
                st.warning("The input contains a symbol outside the alphabet {a,b}.")
    with st.expander("CFG and PDA model"):
        st.markdown("**CFG**")
        st.code("S → aSa | bSb | a | b | ε")
        st.markdown(
            "For an unmarked palindrome, an NPDA pushes symbols from the first half, "
            "nondeterministically guesses the midpoint, then compares and pops symbols "
            "from the second half. For odd lengths it consumes one middle symbol during "
            "the phase change; for even lengths it switches between symbols."
        )
        st.warning(
            "The Python palindrome function checks the reversal property directly. "
            "It is a reference validator, not a literal PDA simulator."
        )

with tab_theory:
    st.subheader("Why CFGs and PDAs?")
    st.markdown(
        "- **Balanced brackets:** the stack remembers arbitrarily nested opening delimiters.
"
        "- **Arithmetic expressions:** grammar structure handles nested parentheses and operator precedence.
"
        "- **Palindromes:** an NPDA can guess the midpoint and compare the two halves using its stack."
    )
    st.markdown("### Finite automata limitation")
    st.write(
        "A finite automaton has finite control and cannot store an unbounded nesting "
        "history or an arbitrarily long first half for later comparison. A PDA adds "
        "a stack, providing the memory required by these context-free models."
    )
    st.markdown("### Student and course details")
    st.write("G Tarun Varma — RA2411026050037")
    st.write("21CSC301T — Formal Language and Automata")

st.divider()
st.caption("Task 3 | CFG and PDA Case Studies | Python + Streamlit")
