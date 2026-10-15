"""从演示文档的大 <script> 里切出顶层语句，算出 makeRecap / makeMakingOf 的传递依赖"""
import re, sys, json
src = open(sys.argv[1], encoding='utf-8').read()
a = src.index('<script>\n', src.index('</style>')) + len('<script>\n'); b = src.index('</script>', a)
lines = src[a:b].split('\n')
chunks, cur, pend = [], None, []
for ln in lines:
    top = ln[:1] not in ('', ' ', '\t', '}', ')', ']')
    if top and (ln.startswith('//') or ln.startswith('/*') or ln.startswith('   ') ):
        pend.append(ln); continue
    if top and not ln.startswith('*') and not ln.startswith(' *'):
        if cur: chunks.append(cur)
        cur = {'lines': pend + [ln]}; pend = []
    else:
        if pend and cur is not None and not top: cur['lines'] += pend; pend = []
        if cur is None: cur = {'lines': []}
        cur['lines'].append(ln)
if cur: chunks.append(cur)
def names(first):
    m = re.match(r'(?:async\s+)?(?:function\*?|class)\s+([\w$]+)', first)
    if m: return [m[1]]
    m = re.match(r'(?:const|let|var)\s+(.*)', first)
    if not m: return []
    out, depth, tok = [], 0, ''
    body = m[1]
    # 只看第一行里深度 0 的 "name =" 
    i = 0; res = []
    seg = ''
    for ch in body:
        if ch in '([{': depth += 1
        elif ch in ')]}': depth -= 1
        if depth == 0 and ch == ',': res.append(seg); seg = ''
        else: seg += ch
    res.append(seg)
    for r in res:
        mm = re.match(r'\s*([\w$]+)\s*=', r)
        if mm: out.append(mm[1])
        mm = re.match(r'\s*\{([^}]*)\}\s*=', r)
        if mm: out += re.findall(r'[\w$]+', mm[1])
    return out
decl = {}
for k, c in enumerate(chunks):
    first = next((l for l in c['lines'] if l[:1] not in ('', ' ', '/', '*')), '')
    c['first'] = first; c['names'] = names(first)
    for n in c['names']: decl.setdefault(n, k)
def body(c): return '\n'.join(c['lines'])
seed = [decl['makeRecap'], decl['makeMakingOf']]
inc, todo = set(), list(seed)
while todo:
    k = todo.pop()
    if k in inc: continue
    inc.add(k)
    txt = re.sub(r"'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`|\"(?:\\.|[^\"\\])*\"", '""', body(chunks[k]))   # 去掉字符串字面量，减少误匹配
    for ident in set(re.findall(r'(?<![\w$.])[A-Za-z_$][\w$]*', txt)):
        if ident in decl and decl[ident] not in inc: todo.append(decl[ident])
order = sorted(inc)
for k in order: print(k, chunks[k]['names'], len(chunks[k]['lines']), chunks[k]['first'][:90])
json.dump({'order': order, 'text': [body(chunks[k]) for k in order]}, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False)
