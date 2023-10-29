
from Flowerchart.flowerchart_node import FlowChartDecisionNode, FlowChartProcessNode, FlowChartNode, FlowChartDelayNode, print_kwargs

from Flowerchart.flowchart_node import *
from Flowerchart.flowchart_system import FlowchartSystem
#phonemics
import eng_to_ipa as p

import random, copy

from functools import partial
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
        
class EyeAcuityTest(FlowchartSystem):
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
            "Default state": ProcessNode(), #Unsure if working
            "Listen for start": IONode(),
            "Check for start": DecisionNode(),
            "Play initial audio": ProcessNode(),
            "Wait for initial audio finish": DelayNode(),
            "Display 6/120 letter": ProcessNode(),
            "Alert PSA": DecisionNode(),
            "Read 6/120": IONode(),
            "Validate 6/120": DecisionNode(),
            "Generic error": ProcessNode(), # Don't define next_node; it is dynamic
            "Generic read": DelayNode(), #Cloneable, to wait for text input
            "Generic validate": DecisionNode(), #Cloneable, to validate input
            "Generic clear screen": ProcessNode(), #Cloneable, to remove letters
            "Display 6/60 and 6/45": ProcessNode(),
        }
        
        def check_for_start(self):
            text = self.context["process_text"]
            text = text.lower()
            if "start" in text or "begin" in text:
                return True
            return False
        
        def generic_error(this: ProcessNode):
            self.eye_acuity_wrapper.play_audio("/tts_recordings/please_try_again.mp3")
            this.next_node = this.previous_node.previous_node
            
        def assign_generic_rv(curr_node, true_node):
            '''
            Generic block to wait for input, then validate input, then clear screen if letters are read correctly
            '''
            my_gr = copy.copy(self.gr)
            my_gv = copy.copy(self.gv)
            my_gcs = copy.copy(self.gcs)
            curr_node.next_node = my_gr
            my_gr.next_node = my_gv
            my_gv.callback = partial(self.check_characters, my_gv)
            my_gv.false_node = self.ge
            my_gv.true_node = my_gcs
            my_gcs.next_node = true_node
        
        self.current_node = self.nodes["Default state"]
        self.ge = self.nodes["Generic error"]
        self.ge.callback = partial(generic_error, self.ge)
        
        # Cloneable to wait for user input
        self.gr = self.nodes["Generic read"]
        self.gr.set_signal_key("process_text")
        
        self.gv = self.nodes["Generic validate"]
        
        self.gcs = self.nodes["Generic clear screen"]
        self.gcs.callback = self.remove_letters
        
        self.nodes["Default state"].callback = partial(self.display_instructions)
        self.nodes["Default state"].next_node = self.nodes["Listen for start"]
        #self.nodes["Listen for start"]: IONode
        self.nodes["Listen for start"].set_signal_key("process_text")
        self.nodes["Listen for start"].next_node = self.nodes["Check for start"]
        
        cfs = self.nodes["Check for start"]
        cfs.callback = partial(check_for_start, cfs)
        cfs.false_node = self.nodes["Default state"]
        cfs.true_node = self.nodes["Play initial audio"]
        
        pia = self.nodes["Play initial audio"]
        pia.callback = partial(self.eye_acuity_wrapper.play_audio, "/tts_recordings/stand_4_meters_away.mp3")
        pia.next_node = self.nodes["Wait for initial audio finish"]
        
        wiaf = self.nodes["Wait for initial audio finish"]
        wiaf.set_signal_key("audio_done")
        wiaf.next_node = self.nodes["Display 6/120 letter"]
        
        d6120 = self.nodes["Display 6/120 letter"]
        d6120.callback = partial(self.display_characters, (1, "6/120"))
        assign_generic_rv(d6120, self.nodes["Display 6/60 and 6/45"])
        
        d660645 = self.nodes["Display 6/60 and 6/45"]
        d660645.callback = partial(self.display_characters, (1, "6/60"), (1, "6/45"))
        assign_generic_rv(d660645, d660645)
        
    '''
    Methods used for acuity test display
    '''
    def display_instructions(self, **kwargs):
        # If kwargs has no parameter "text", text will have a default value of "Insert text"
        text = "Insert text" if ("text" not in kwargs) else kwargs["text"]
    def remove_letters(self):
            javascript = """
            var lettersContainer = document.querySelector(".letters");

            // Remove all child elements (paragraphs) from the "letters" container
            while (lettersContainer.firstChild) {
                lettersContainer.removeChild(lettersContainer.firstChild);
            }
            """
            self.eye_acuity_wrapper.run_javascript(javascript)
    def display_characters(self, *chara_tuples):
        '''
        (num_of_characters, vam_size)
        <!> Random positioning of these characters, no overlap
        '''
        self.characters_displayed = {}
        for i in chara_tuples:
            num_of_characters = i[0]
            vam_size = i[1]
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
        
    def check_characters(self, node):
        # <!> Order currently not maintained
        context = node.context
        print(node)
        print(node.next_node)
        print("Context is ", context)
        self.characters_score = {}
        user_input = context["process_text"]
        o_user_input = user_input
        user_input = user_input.lower()
        user_input = user_input.replace("-"," ")
        
        # Bandaid for issue: "Letters stuck together may be considered as word, hence ipa conversion fails"
        total_char_length = 0
        # Calculate total length of characters
        for vam_size, characters in self.characters_displayed.items():
            total_char_length+=len(characters)
        if len(user_input) <= total_char_length:
            user_input = list(user_input)
        else:
            user_input = user_input.split(" ")
        ipa_user_input = []
        for i in user_input:
            ipa_user_input.append(p.convert(i))
        om_user_input = user_input
        # Tabulate score for each characters
        for vam_size,characters in self.characters_displayed.items():
            self.characters_score[vam_size] = 0
            for cd in characters:
                # Get the ipa(s) of the displayed character
                ipas = self.character_ipa_map[cd]
                for ipa in ipas:
                    if ipa in ipa_user_input:
                        # If user said character, score increases
                        self.characters_score[vam_size] += 1
                        ipa_user_input.remove(ipa)
                        break
        
        for vam_size, score in self.characters_score.items():
            if len(self.characters_displayed[vam_size]) > score:
                print("<Check characters> False")
                print(self.characters_displayed)
                print(self.characters_score)
                
                print(o_user_input)
                print(om_user_input)
                return False
        return True
        
    
    def please_try_again(self, **kwargs):
        node: FlowChartDecisionNode = kwargs["flowerchart_node"]
        self.eye_acuity_wrapper.play_audio("/tts_recordings/please_try_again.mp3")
        
        # Give another chance
        node.false_node = node
        
        
    def start_instructions(self, **kwargs):
        pass
        '''
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
        '''

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
    eat.run()
    #eat.old_node = eat.current_node
    #while eat.old_node == eat.current_node:
    while eat.current_node is not None:
        print("Current node:", eat.current_node)
        #s_key = input("Enter signal key: ")
        s_data = input("Enter signal data: ")
        eat.signal("process_text", s_data)
        eat.signal("audio_done", s_data)