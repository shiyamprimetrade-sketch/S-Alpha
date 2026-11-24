from s_alpha.strategy import train, evaluate

TRAIN = [("calculator!", "calculator"), ("temperature", "temperature"), ("counter?", "counter"), ("chess", None)]
HELD_OUT = [("Build addition.", "addition"), ("Build a calculator", "calculator"), ("counter!", "counter"), ("temperature?", "temperature"), ("chess!", None), ("calculator counter", None)]

def benchmark():
    selected = train(TRAIN)
    return {"selected":selected,"raw":evaluate(HELD_OUT,"raw"),"selected_score":evaluate(HELD_OUT,selected),"total":len(HELD_OUT)}

if __name__ == "__main__":
    print(benchmark())
