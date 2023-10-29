
from Flowerchart.flowerchart_node import FlowChartDecisionNode, FlowChartProcessNode, FlowChartNode, FlowChartDelayNode, print_kwargs

from Flowerchart.flowchart_node import *
from Flowerchart.flowchart_system import *
#phonemics
import eng_to_ipa as p

import random, copy
# This class contains the method run_javascript and play_audip which HTMLWindow will implement
# HTMLWindow will override run_javascript and play_audio with actual implementation
# This class is used for testing purposes

'''
Still need pinhole support
'''
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
        
        # <!> Need to use a dict to store sizes of characters
        self.characters_displayed = {}
        self.characters_score = {}
        
        # <!> Map Visual Acuity Measurement to font size (cm can be used)
        self.vam_to_font_size = {
            "6/120": "2cm",
            "6/60": "1.5cm",
            "6/45": "1cm"
        }
        
        self.generable_characters = ['C', 'D', 'E', 'F', 'L', 'O', 'P', 'T', 'Z']
        self.generable_characters_ipa = ["si", "di", 'i', 'ɛf', 'ɛl', 'oʊ', 'pi', 'ti', 'zi']

        self.character_ipa_map = {
            "C": ["si"], "D": ["di"], "E": ['i'], 
            "F": ['ɛf'],"L": ['ɛl'],"O": ['oʊ'],
            "P": ['pi'],"T": ['ti'],"Z": ['zi', 'zæk']
        }
        # <!> Need to map generable_characters to ipa
        
        self.eye_acuity_wrapper = eye_acuity_wrapper
        
        self.nodes = {
            "Default state": FlowChartProcessNode(), #Unsure if working
            "Await instructions": FlowChartDecisionNode(),
            "Play initial audio": FlowChartProcessNode(),
            "Wait for instructions to finish": FlowChartDelayNode(),
            "Display 6/120 letter": FlowChartProcessNode(),
            "Alert PSA": FlowChartDecisionNode(),
            "Validate 6/120": FlowChartDecisionNode(),
            "Display 6/60 and 6/45": FlowChartProcessNode(),
            "Validate 6/60 and 6/45": FlowChartDecisionNode()
        }
        
        self.current_node = self.nodes["Default state"]
        self.nodes["Default state"].set_callbacks( [ (self.display_instructions, {}), 
                                                    (print_kwargs, {"output": "Please enter start or begin."}) 
                                                    ] )
        self.nodes["Default state"].next_node = self.nodes["Await instructions"]
        
        self.nodes["Await instructions"].set_condition_callbacks( [ (self.start_instructions, {}) ] )
        self.nodes["Await instructions"].false_node = self.nodes["Default state"]
        self.nodes["Await instructions"].next_node = self.nodes["Play initial audio"]
        
        self.nodes["Play initial audio"].set_callbacks([
            (self.play_audio, {"audio_file_path": "/tts_recordings/stand_4_meters_away.mp3"})
        ])
        self.nodes["Play initial audio"].next_node = self.nodes["Wait for instructions to finish"]
        
        # Delay node to make sure instructions finish playing
        self.nodes["Wait for instructions to finish"].next_node = self.nodes["Display 6/120 letter"]
        
        # Display 6/120 letter
        self.nodes["Display 6/120 letter"].set_callbacks( [(self.display_characters, 
                                                            {"c_array":[{"num_of_characters": 1,"vam_size": "6/120"}]
                                                             }),
                                                        ] )
        self.nodes["Display 6/120 letter"].next_node = self.nodes["Validate 6/120"]
        
        # Validate 6/120
        self.nodes["Validate 6/120"].set_condition_callbacks( [ (self.check_characters, {})])
        self.nodes["Validate 6/120"].set_false_callbacks( [ 
                                                           (self.please_try_again,{}),
                                                           (print_kwargs, {"output": "ALERT PSA"})])
        
        def remove_letters(**kwargs):
            javascript = """
            var lettersContainer = document.querySelector(".letters");

            // Remove all child elements (paragraphs) from the "letters" container
            while (lettersContainer.firstChild) {
                lettersContainer.removeChild(lettersContainer.firstChild);
            }
            """
            self.eye_acuity_wrapper.run_javascript(javascript)
            
        self.nodes["Validate 6/120"].set_true_callbacks([ (remove_letters,{})
                                                          ])
        self.nodes["Validate 6/120"].next_node = self.nodes["Display 6/60 and 6/45"]
        
        # Display 6/60 and 6/45
        self.nodes["Display 6/60 and 6/45"].set_callbacks( [(self.display_characters, 
                                                            {"c_array":[
                                                                {"num_of_characters": 1,"vam_size": "6/60"},
                                                                {"num_of_characters": 1, "vam_size": "6/45"}
                                                            ]}),
                                                           (print_kwargs, {"output": "Display 6/120 letter"}) ] )
        self.nodes["Display 6/60 and 6/45"].next_node = self.nodes["Validate 6/120"]
        
        # Validate 6/60 and 6/45
        self.nodes["Validate 6/60 and 6/45"] = copy.copy(self.nodes["Validate 6/120"])
        self.nodes["Validate 6/60 and 6/45"].next_node = self.nodes["Display 6/60 and 6/45"]
        
        #self.nodes["Validate 6/60"].next_node = self.nodes["Play initial audio"]
        #self.nodes["Validate 6/120"].false_node = self.nodes[""]
    
    
    # process nodes
    def execute_process(self):
        self.current_node: FlowChartProcessNode = self.current_node.execute()
    
    # decision nodes
    def execute_decision(self, input):
        self.current_node: FlowChartDecisionNode = self.current_node.execute(input)
        
    # delay nodes
    def execute_delay(self):
        self.current_node: FlowChartDelayNode = self.current_node.execute()
    '''
    Methods used for acuity test display
    '''
    def display_instructions(self, **kwargs):
        # If kwargs has no parameter "text", text will have a default value of "Insert text"
        text = "Insert text" if ("text" not in kwargs) else kwargs["text"]
        
    def display_characters(self, **kwargs):
        '''
        Method only supports 1 size, should be revamped to support
        <!> Multiple characters of different sizes
        <!> Random positioning of these characters, no overlap
        '''
        for i in kwargs["c_array"]:
            self.characters_displayed = {}
            num_of_characters = i["num_of_characters"]
            vam_size = i["vam_size"]
            font_size = self.vam_to_font_size[vam_size]
            # <!> Generate characters, based on num_of_characters
            #num_of_characters = kwargs["num_of_characters"]
            print("Generate ", num_of_characters, " characters")
            
            chosen_ones = []
            chosen_ones = random.sample(self.generable_characters, num_of_characters)
            self.characters_displayed[vam_size] = chosen_ones
            chosen_ones = " " .join(chosen_ones)
            
            # <!> Write Javascript to generate characters of font size
            print("Characters of font size ", font_size)
            
            javascript = f"""
            // Get the <p> element under the "letters" class
            var lettersParagraph = document.querySelector(".letters");

            var para = document.createElement('p');
            // Define the text you want to set
            var newText = "{chosen_ones}";

            // Set the text content of the <p> element
            para.textContent = newText;
            
            para.style.fontSize = "{font_size}";
            lettersParagraph.appendChild(para);
            """
            
            # <!> Call run_javascript method of eye_acuity_wrapper
            self.eye_acuity_wrapper.run_javascript(javascript)
        
    def check_characters(self, **kwargs):
        self.characters_score = {}
        user_input = kwargs["conditional_var"]
        user_input = p.convert(user_input).lower()
        user_input = user_input.replace("-"," ")
        
        # Bandaid for issue: "Letters stuck together may be considered as word, hence ipa conversion fails"
        total_char_length = 0
        for vam_size, characters in self.characters_displayed.items():
            total_char_length+=len(characters)
        if len(user_input) == total_char_length:
            user_input = user_input.split("")
        else:
            user_input = user_input.split(" ")
        
        # Tabulate score for each characters
        for vam_size,characters in self.characters_displayed.items():
            self.characters_score[vam_size] = 0
            for cd in characters:
                # Get the ipa(s) of the displayed character
                ipas = self.character_ipa_map[cd]
                for ipa in ipas:
                    if ipa in user_input:
                        # If user said character, score increases
                        self.characters_score[vam_size] += 1
                        user_input.remove(ipa)
                        break
        
        for vam_size, score in self.characters_score.items():
            if len(self.characters_displayed[vam_size]) > score:
                return False
        return True
        
    
    def please_try_again(self, **kwargs):
        node: FlowChartDecisionNode = kwargs["flowerchart_node"]
        self.eye_acuity_wrapper.play_audio("/tts_recordings/please_try_again.mp3")
        
        # Give another chance
        node.false_node = node
        
        
    def start_instructions(self, **kwargs):
        user_input = kwargs["conditional_var"]
        #html_window = kwargs["html_window"]
        if "start" in user_input.lower() or "begin" in user_input.lower():
            if not self.in_test:
                print("〖 START 〗")
                self.in_test = True
            else:
                print("Already〖 STARTED 〗")
            return True
        return False

    def play_audio(self, **kwargs):
        audio_file_path = kwargs["audio_file_path"]
        self.eye_acuity_wrapper.play_audio(audio_file_path)

if __name__ == "__main__":
    #app = QApplication(sys.argv)
    #window = HTMLWindow()
    #window.show()
    #sys.exit(app.exec_())
    jr = EyeAcuityWrapper()
    eat = EyeAcuityTest(jr)
    eat.current_node = eat.current_node.execute()
    #eat.old_node = eat.current_node
    #while eat.old_node == eat.current_node:
    while eat.current_node is not None:
        if isinstance(eat.current_node,FlowChartDecisionNode):
            eat.current_node = eat.current_node.execute(input("Enter input: "))
        elif isinstance(eat.current_node,FlowChartDelayNode):
            print("<Delay node> Pretending delay has passed")
            eat.current_node = eat.current_node.execute()