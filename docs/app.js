const $ = (id) => document.getElementById(id);
document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((b) => b.classList.toggle("active", b === button));
    document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("active", p.id === button.dataset.tab));
  });
});
function result(id, accepted, yes, no) {
  const el = $(id); el.className = "result " + (accepted ? "good" : "bad"); el.textContent = accepted ? yes : no;
}
function validateBrackets(s) {
  const pairs = {"(":")","[":"]","{":"}"}, closers = new Set(Object.values(pairs));
  const stack = [], trace = []; let accepted = s.length > 0;
  if (!s.length) trace.push("Reject: the language excludes the empty string.");
  for (const ch of s) {
    if (pairs[ch]) { stack.push(ch); trace.push(`Read '${ch}': push; stack = [${stack.join(" ")}]`); }
    else if (closers.has(ch)) {
      if (!stack.length) { trace.push(`Read '${ch}': reject; no opener is available.`); accepted = false; break; }
      const top = stack[stack.length-1];
      if (pairs[top] !== ch) { trace.push(`Read '${ch}': reject; stack top '${top}' expects '${pairs[top]}'.`); accepted = false; break; }
      stack.pop(); trace.push(`Read '${ch}': matching pop; stack = [${stack.join(" ")}]`);
    } else { trace.push(`Reject: unsupported character '${ch}'.`); accepted = false; break; }
  }
  if (accepted && stack.length) { trace.push(`Reject: unmatched openers remain [${stack.join(" ")}].`); accepted = false; }
  if (accepted) trace.push("Input consumed and stack empty: ACCEPT.");
  return {accepted,trace};
}
$("bracket-run").addEventListener("click", () => {
  const r = validateBrackets($("bracket-input").value);
  result("bracket-result",r.accepted,"Accepted — the brackets are balanced.","Rejected — the string is not in the balanced-bracket language.");
  $("bracket-trace").textContent = r.trace.join("\n");
});
function tokenize(src) {
  const out=[]; let i=0;
  while(i<src.length) {
    if (/\s/.test(src[i])) {i++;continue;}
    if (src.startsWith("id",i) && (i+2===src.length || !/[A-Za-z0-9_]/.test(src[i+2]))) {out.push("id");i+=2;continue;}
    if ("+*()".includes(src[i])) {out.push(src[i]);i++;continue;}
    throw Error(`invalid token at position ${i}: '${src[i]}'`);
  }
  return out;
}
function parseExpression(src) {
  let tokens; try {tokens=tokenize(src);} catch(e){return {ok:false,trace:[`reject: ${e.message}`]};}
  tokens.push("$"); let pos=0; const trace=[];
  const look=()=>tokens[pos];
  const consume=(t)=>{if(look()!==t)throw Error(`expected '${t}', found '${look()}'`);trace.push(`match ${t}`);pos++;};
  function factor(){if(look()==="id")consume("id");else if(look()==="("){consume("(");expr();consume(")");}else throw Error(`expected id or '(', found '${look()}'`);}
  function term(){factor();while(look()==="*"){consume("*");factor();}}
  function expr(){term();while(look()==="+"){consume("+");term();}}
  try {expr();if(look()!=="$")throw Error(`unexpected token '${look()}'`);trace.push("accept");return {ok:true,trace};}
  catch(e){trace.push(`reject: ${e.message}`);return {ok:false,trace};}
}
$("expression-run").addEventListener("click",()=>{
  const r=parseExpression($("expression-input").value);
  result("expression-result",r.ok,"Accepted — the expression is syntactically valid.","Rejected — the expression is not well formed.");
  $("expression-trace").textContent=r.trace.join("\n");
});
$("palindrome-run").addEventListener("click",()=>{
  const s=$("palindrome-input").value, valid=/^[ab]*$/.test(s), accepted=valid && s===Array.from(s).reverse().join("");
  result("palindrome-result",accepted,"Accepted — the string is a palindrome over {a,b}.","Rejected — the string is not a palindrome over {a,b}.");
  if(!valid) $("palindrome-trace").textContent="Reject: input contains a symbol outside the alphabet {a,b}.";
  else if(!accepted) $("palindrome-trace").textContent="No derivation: the string differs from its reverse.";
  else {
    const steps=["S"]; let inner=s;
    while(inner.length>=2){const ch=inner[0];steps.push(`${ch} S ${ch}  (S → ${ch}S${ch})`);inner=inner.slice(1,-1);}
    if(inner==="a"||inner==="b")steps.push(`${inner}  (S → ${inner})`);else steps.push("ε  (S → ε)");
    $("palindrome-trace").textContent=steps.join("\n");
  }
});
$("bracket-run").click(); $("expression-run").click(); $("palindrome-run").click();
