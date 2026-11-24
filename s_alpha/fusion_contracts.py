"""Fixed acceptance examples, separate from candidate generation."""
CONTRACTS={
    "calculator_add":(("2","3","5"),("-4","1","-3"),("0.1","0.2","0.3"),("0","0","0")),
    "inventory_adjust":(("10","5","15"),("10","-3","7"),("0","0","0"),("2","-3","REJECT")),
}
def evaluate(contract, candidate):
    rows=[]
    for a,b,expected in CONTRACTS[contract]:
        try:
            actual=candidate(a,b)
        except ValueError:
            actual="REJECT"
        rows.append({"inputs":[a,b],"expected":expected,"actual":actual,"passed":actual==expected})
    return rows
