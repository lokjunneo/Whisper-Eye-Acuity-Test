from __future__ import annotations

# Import typings
from typing import Callable, Any

from functools import partial
class FlowchartNode:
    def __init__(self, attributes=None, context={}, next_node: FlowchartNode = None):
        self.attributes = attributes
        self.context = context
        self.next_node = next_node
        self.previous_node = None
    
    def _to_next_node(self):
        if self.next_node is not None:
            self.next_node.context = self.context
            self.next_node.previous_node = self
            
            if isinstance(self.next_node, CallableNode):
                return self.next_node._callback()
        return self.next_node
    
    def set_next_node(self, next_node: FlowchartNode):
        self.next_node = next_node
    
class CallableNode(FlowchartNode):
    callback: Callable
    def __init__(self, attributes=None, context={}, next_node: FlowchartNode = None):
        super().__init__(attributes=attributes, context=context, next_node=next_node)
    
    # Override this
    def callback(self):
        pass
    
    def set_callback(self, callback):
        self.callback = callback
    
    def _callback(self):
        self.callback()
        return self._to_next_node()

class ProcessNode(CallableNode):
    # Override this
    def callback(self):
        pass
    pass
        
class DecisionNode(CallableNode):
    
    def __init__(self, attributes=None, context={}, 
                false_node: FlowchartNode = None, 
                true_node: FlowchartNode = None):
        super().__init__(attributes=attributes, context=context, next_node=None)
        self.false_node = false_node
        self.true_node = true_node
        
    # Override this
    def callback(self):
        pass
    def set_true_node(self, true_node: FlowchartNode):
        self.true_node = true_node
    def set_false_node(self, false_node: FlowchartNode):
        self.false_node = false_node
    
    def _callback(self):
        if self.callback() == True:
            self.next_node = self.true_node
        else:
            self.next_node = self.false_node
        return self._to_next_node()

class SignalNode(FlowchartNode):
    def __init__(self, attributes=None, context={}, next_node: FlowchartNode = None, signal_key = None):
        super().__init__(attributes=attributes, context=context, next_node=next_node)
        self.signal_key = None
    def _process_signal(self, signal_key, *signal_data):
        if self.signal_key == signal_key:
            if len(signal_data) == 1:
                self.context[signal_key] = signal_data[0]
            return self._to_next_node()
        
        # Current node is self again, so system will wait for signal
        return self
    
    #Override this
    def process_signal(self, signal_key, *signal_data):
        pass
    def set_signal_key(self, signal_key):
        self.signal_key = signal_key
    
class IONode(SignalNode):
    pass

class DelayNode(SignalNode):
    pass


if __name__ == '__main__':
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
    
    #delay_n.set_next_node(pass_pn)
    delay_n.set_signal_key("Surprise!")
    
    current_node = display_qn._callback()
    print(current_node)
    
    
    
        

        
