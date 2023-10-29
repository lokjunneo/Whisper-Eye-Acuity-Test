
from Flowerchart.flowerchart_node import FlowChartDecisionNode, FlowChartProcessNode, FlowChartNode, print_kwargs

# This class contains the method run_javascript and play_audip which HTMLWindow will implement
# HTMLWindow will override run_javascript and play_audio with actual implementation
# This class is used for testing purposes
class EyeAcuityWrapper:
    def run_javascript(self, javascript):
        print("Page will run the following Javascript: ", javascript)
        
    def play_audio(self, relative_audio_location):
        print("Audio at '", relative_audio_location, "' will be played")
        
class EyeAcuityTest():
    def __init__(self, eye_acuity_wrapper: EyeAcuityWrapper):
        self.in_test = False
        
        # Scanning success?
        self.scanning = 1
        
        self.eye_acuity_wrapper = eye_acuity_wrapper
        
        self.nodes = {
            "Default state": FlowChartProcessNode(), #Unsure if working
            "Await instructions": FlowChartDecisionNode(),
            "Display 6/120 letter": FlowChartProcessNode(),
            "Read out display letter": FlowChartDecisionNode()
        }
        
        self.current_node = self.nodes["Default state"]
        self.nodes["Default state"].set_callbacks( [ (self.display_instructions, {"text": " Funny "}), 
                                                    (print_kwargs, {"output": "Please enter start or begin."}) 
                                                    ] )
        self.nodes["Default state"].next_node = self.nodes["Await instructions"]
        
        self.nodes["Await instructions"].set_condition_callbacks( [ (self.start_instructions, {}) ] )
        self.nodes["Await instructions"].set_false_callbacks( [ (print_kwargs, {"output": "Didn't receive start or begin"} ) ] )
        self.nodes["Await instructions"].set_true_callbacks( [ (print_kwargs, {"output": "Beginning"} ) ] )
        self.nodes["Await instructions"].false_node = self.nodes["Default state"]
        self.nodes["Await instructions"].next_node = self.nodes["Display 6/120 letter"]
        
        self.nodes["Display 6/120 letter"].set_callbacks( [ (print_kwargs, {"output": "Display 6/120 letter"}) ] )
        
    def display_instructions(self, **kwargs):
        # If kwargs has no parameter "text", text will have a default value of "Insert text"
        text = "Insert text" if ("text" not in kwargs) else kwargs["text"]
        
        # <!> Work on javascript to modify instructions header
        #   Instructions header will see very few use however
        javascript = "console.log('I will display '" + text + "');"
        
        self.eye_acuity_wrapper.run_javascript(javascript)
        
    #def display_characters(self, num_of_characters, font_size):
    def display_characters(self, **kwargs):
        
        # <!> Generate characters, based on num_of_characters
        print("Generate ", kwargs["num_of_characters"], " characters")
        
        # <!> Write Javascript to generate characters of font size
        print("Characters of font size ", kwargs["font_size"])
        javascript = "console.log('Generated Javascript')"
        
        # <!> Call run_javascript method of eye_acuity_wrapper
        self.eye_acuity_wrapper.run_javascript(javascript)
        
    def start_instructions(self, **kwargs):
        user_input = kwargs["conditional_var"]
        #html_window = kwargs["html_window"]
        if "start" in user_input.lower() or "begin" in user_input.lower():
            if not self.in_test:
                print("〖 START 〗")
                self.eye_acuity_wrapper.play_audio("/tts_recordings/stand_4_meters_away.mp3")
                self.in_test = True
            return True
        return False


if __name__ == "__main__":
    #app = QApplication(sys.argv)
    #window = HTMLWindow()
    #window.show()
    #sys.exit(app.exec_())
    jr = EyeAcuityWrapper()
    eat = EyeAcuityTest(jr)
    eat.current_node = eat.current_node.execute()
    eat.old_node = eat.current_node
    while eat.old_node == eat.current_node:
        eat.current_node = eat.current_node.execute(input("Enter input: "))