from .flowchart_node import *

class FlowchartSystem:
    def __init__(self, nodes = [], start_node = None):
        self.nodes = nodes
        self.current_node = start_node
    
    def run(self):
        if self.current_node is not None:
            if isinstance(self.current_node, CallableNode):
                self.current_node = self.current_node._callback()
    
    def signal(self, signal_key, *signal_data):
        if isinstance(self.current_node, SignalNode):
            self.current_node = self.current_node._process_signal(signal_key, *signal_data)
            
            

if __name__ == '__main__':
    from flowchart_node import *
    #foo.bark = new_bark.__get__(foo, Dog)
    def test_print(parameter):
        print(parameter)
    def prompt_input(self: ProcessNode,parameter):
        user_input = input(parameter)
        self.context["user_input"] = user_input
    def verify_input(self: ProcessNode):
        if ("a" in self.context["user_input"]):
            return True
        return False
    
    def send_signal(target_node, key):
        if isinstance(target_node, SignalNode):
            target_node._process_signal(key)
    
    display_qn = ProcessNode()
    prompt_pn = ProcessNode()
    verify_pn = DecisionNode()
    
    pass_pn = ProcessNode()
    fail_pn = ProcessNode()
    
    signal_pn = ProcessNode()
    
    delay_n = DelayNode()
    
    # No need to pass self in
    display_qn.callback = partial(test_print, "Hello")
    display_qn.set_next_node(prompt_pn)
    
    # If reference to self is required
    prompt_pn.callback = partial(prompt_input, prompt_pn, "input 'a': ")
    prompt_pn.set_next_node(verify_pn)
    
    # Set true or false node
    verify_pn.callback = partial(verify_input, verify_pn)
    verify_pn.set_true_node(pass_pn)
    verify_pn.set_false_node(fail_pn)
    
    fail_pn.callback = partial(test_print, "Try again")
    fail_pn.set_next_node(display_qn)
    
    
    pass_pn.callback = partial(test_print, "Congrats! You reached the end!")
    pass_pn.set_next_node(signal_pn)
    
    signal_pn.callback = partial(send_signal, delay_n, "Surprise!")
    signal_pn.set_next_node(delay_n)
    
    delay_n.set_signal_key("Surprise!")
    
    fcs = FlowchartSystem(start_node = display_qn)
    fcs.run()
    print(fcs.current_node)
    