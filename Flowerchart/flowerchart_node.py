'''
Possible improvements: https://stackoverflow.com/questions/2627002/whats-the-pythonic-way-to-use-getters-and-setters

Need to raise Errors for easier debugging
'''
# Required import for function declaration of own class type
# e.g. 
# In FlowChartNode, 
# def set_previous_node(self, previous_node: FlowChartNode):
from __future__ import annotations

# Import typings
from typing import Callable, Any
class FlowChartNode:
    # <!> Consider using kwargs, or inheritance will be a nightmare
    def __init__(self, self_attributes=None, next_node: FlowChartNode = None, context = None):
                #executable_methods: list[tuple[Callable,dict]] = None):
        
        # Define self attributes of Node, such as name, id, ...
        # This attributes belong to the Node itself
        self.self_attributes = self_attributes
        
        self.type = self.__class__
        self.previous_node: FlowChartNode = None # automatically assigned
        self.next_node: FlowChartNode = next_node
        
        # Context or data that will be carried over from one Node to another
        # In other words, you store your own variables here
        self.context = context  

        #self.executable_methods = executable_methods
    '''
    def set_previous_node(self, previous_node: FlowChartNode):
        self.previous_node = previous_node
    '''
    def _set_callbacks(self, variable_name, callbacks: list[tuple[Callable, dict]]):
        '''
        Reusable method to set executable_methods to certain variable names
        '''
        # No error handling, number of items in methods should be same as that of methods_kwargs
        #self.executable_methods = [methods,methods_kwargs]  
        #self.executable_methods = executable_methods
        setattr(self, variable_name, callbacks)
        
        for method_tuple in getattr(self, variable_name):
            
            # Add context into one of the parameters
            # <!> Find a key that is guaranteed unique (perhaps with class name)
            
            #print(method_tuple[1])
                
            method_kwargs = method_tuple[1]
            method_kwargs["flowerchart_node"] = self
    
    def _execute(self, callback_var_name):
        for callback_tuple in getattr(self, callback_var_name):
            callback: Callable = callback_tuple[0]
            callback_kwargs: dict = callback_tuple[1]
            
            # Unpack method_kwargs
            callback(**callback_kwargs)
    
    def _go_to_node(self, node):
        if node is not None:
            # Pass context to next node
            node.set_context(self.context)
            
            # Set previous node of next node to self
            node.previous_node = self
            
            # Return the next_node to be executed
            # If next node is also a process node, go on and execute that as well
            if isinstance(node,FlowChartProcessNode):
                return node.execute()
        
        return self.next_node
    def _go_to_next_node(self):
        return self._go_to_node(self.next_node)
        
    def set_next_node(self, next_node: FlowChartNode):
        self.next_node = next_node
    
    def set_context(self, context):
        self.context = context
    
class FlowChartProcessNode(FlowChartNode):
    # <!> Add constructor that accepts executable_methods
    
    #
    def set_executable_methods(self, callbacks: list[tuple[Callable, dict]] ):
        
        self._set_callbacks("callbacks", callbacks)
    
    def execute(self) -> FlowChartNode:
        # execute currently does not pass in FlowChartNode's self into the methods
        '''
        Execute the methods in self.executable methods
        Then return next_node
        (Does not automatically execute next_node)
        '''
        self._execute("callbacks")
        
        # Returns next_node, None if not assigned
        return self._go_to_next_node()
    
class FlowChartDecisionNode(FlowChartNode):
    
    '''
    condition_callbacks
    false_callbacks
    true_callbacks
    false_node: Next node if condition is false
    '''
    
    def __init__(self, self_attributes=None, next_node: FlowChartNode = None, false_node: FlowChartNode = None, context = None):
        super().__init__(self_attributes=self_attributes, next_node=next_node, context=context)
        
    def set_condition_callbacks(self, condition_callbacks: list[tuple[Callable, dict]] ):
        
        self._set_callbacks("condition_callbacks", condition_callbacks)
    
    def set_false_callbacks(self, false_callbacks: list[tuple[Callable, dict]] ):
        
        self._set_callbacks("false_callbacks", false_callbacks)
    
    def set_true_callbacks(self, true_callbacks: list[tuple[Callable, dict]] ):
        
        # Sets self.true_callbacks = true_callbacks, and stores self as value to flowerchart_node key
        self._set_callbacks("true_callbacks", true_callbacks)
    
    def set_false_node(self, false_node):
        self.false_node = false_node
        
    def check_condition(self, conditional_var):
        #self.condition_callbacks = list[tuple[Callable, dict]] 
        for tuple in self.condition_callbacks:
            callback: Callable = tuple[0]
            callback_kwargs: dict = tuple[1]
            callback_kwargs["conditional_var"] = conditional_var
            if callback(**callback_kwargs) is not True:
                return False
        return True
    
    def execute(self, conditional_var):
        if self.check_condition(conditional_var) is not False:
            self._execute("true_callbacks")
            # Returns next_node, None if not assigned
            return self._go_to_next_node()
        else:
            self._execute("false_callbacks")
            return self._go_to_node(self.false_node)
        
        
        
        
# Testing method to print out keyword arguments
def print_kwargs(**kwargs):
    for key, value in kwargs.items():
        print(key, ":", value)
    
def check_user_input(**kwargs):
    user_input = kwargs["conditional_var"]
    if "a" in user_input:
        return True
    else:
        return False
if __name__ == "__main__":
    p1 = FlowChartProcessNode()
    p1.set_executable_methods( [ (print_kwargs, {"a": "haha"}) ] )
    p2 = FlowChartProcessNode(next_node=p1)
    p2.set_executable_methods([(print_kwargs, {"b": "one"})])
    d1 = FlowChartDecisionNode()
    d1.set_condition_callbacks([(check_user_input, {})])
    d1.set_false_callbacks([(print_kwargs, {"a": "no a"})])
    d1.set_true_callbacks([(print_kwargs, {"p": "a detected"})])
    p1.next_node = d1
    d1.set_false_node(p2)
    p2.execute()
    
    while d1.execute(input("type a: ")) is not None:
        #print(d1.execute(input("type a: ")))
        pass