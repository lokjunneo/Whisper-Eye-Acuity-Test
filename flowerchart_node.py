'''
Possible improvements: https://stackoverflow.com/questions/2627002/whats-the-pythonic-way-to-use-getters-and-setters
'''
# Required import for function declaration of own class type
# e.g. 
# In FlowChartNode, 
# def set_previous_node(self, previous_node: FlowChartNode):
from __future__ import annotations

# Import typings
from typing import Callable
class FlowChartNode:
    # <!> Consider using kwargs, or inheritance will be a nightmare
    def __init__(self, self_attributes=None, next_node: FlowChartNode = None, context = None, 
                executable_methods: list[tuple[Callable,dict]] = None):
        
        # Define self attributes of Node, such as name, id, ...
        # This attributes belong to the Node itself
        self.self_attributes = self_attributes
        
        self.type = self.__class__
        self.previous_node: FlowChartNode = None # automatically assigned
        self.next_node: FlowChartNode = next_node
        
        # Context or data that will be carried over from one Node to another
        # In other words, you store your own variables here
        self.context = context  
        
        self.executable_methods = executable_methods
    
    def set_executable_methods(self, executable_methods: list[tuple[Callable, dict]] ):
        '''
        Methods should have same length as methods_kwargs
        '''
        
        # No error handling, number of items in methods should be same as that of methods_kwargs
        #self.executable_methods = [methods,methods_kwargs]  
        self.executable_methods = executable_methods
        
        for method_tuple in executable_methods:
            
            # Add context into one of the parameters
            # <!> Consider passing the entire FlowchartNode in (i.e. self)
            # <!> Find a key that is guaranteed unique (perhaps with class name)
            
            method_kwargs = method_tuple[1]
            method_kwargs["flowchart_context"] = self.context 
    '''
    def set_previous_node(self, previous_node: FlowChartNode):
        self.previous_node = previous_node
    '''
    
    def set_next_node(self, next_node: FlowChartNode):
        self.next_node = next_node
    
    def set_context(self, context):
        self.context = context
    
class FlowChartProcessNode(FlowChartNode):
        
    def execute(self) -> FlowChartNode:
        # execute currently does not pass in FlowChartNode's self into the methods
        '''
        Execute the methods in self.executable methods
        Then return next_node
        (Does not automatically execute next_node)
        '''
        for method_tuple in self.executable_methods:
            method: Callable = method_tuple[0]
            method_kwargs: dict = method_tuple[1]
            
            # Unpack method_kwargs
            method(**method_kwargs)
        if self.next_node is not None:
            # Pass context to next node
            self.next_node.set_context(self.context)
            
            # Set previous node of next node to self
            self.next_node.previous_node = self
            
            # Return the next_node to be executed
            # If next node is also a process node, go on and execute that as well
            if isinstance(self.next_node,FlowChartProcessNode):
                return self.next_node.execute()
        
        return self.next_node
    
class FlowChartDecisionNode(FlowChartNode):
    pass
        
# Testing method to print out keyword arguments
def print_kwargs(**kwargs):
    print(kwargs)
    
if __name__ == "__main__":
    p1 = FlowChartProcessNode()
    p1.set_executable_methods([(print_kwargs, {"banana": "haha"})])
    p2 = FlowChartProcessNode(next_node=p1)
    p2.set_executable_methods([(print_kwargs, {"first": "one"})])
    p2.execute()