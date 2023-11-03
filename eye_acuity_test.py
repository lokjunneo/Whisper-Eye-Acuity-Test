
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
        
        # <!> Map Visual Acuity Measurement to font size (cm can be used)
        self.vam_to_font_size = {
            "6/120": "2cm",
            "6/60": "1.5cm",
            "6/45": "1cm"
        }
        
        self.generable_characters = ['C', 'D', 'E', 'F', 'L', 'O', 'P', 'T', 'Z']
        #self.generable_characters_ipa = ["si", "di", 'i', 'ɛf', 'ɛl', 'oʊ', 'pi', 'ti', 'zi']

        self.character_ipa_map = {
            "C": ["si"], "D": ["di"], "E": ['i'], 
            "F": ['ɛf'],"L": ['ɛl'],"O": ['oʊ'],
            "P": ['pi'],"T": ['ti'],"Z": ['zi', 'zæk', 'zek*','zɛk','zeee']
        }
        
        # Store all ipa of all letters
        from string import ascii_lowercase
        self.ipa_letters = []
        for i in ascii_lowercase: self.ipa_letters.append(p.convert(i))
        self.ipa_letters += ['zæk', 'zek*','zɛk','zeee'] # All alternate pronounciation of z
        print("List of ipa_letters initialised with values: ", self.ipa_letters)
        # <!> Need to map generable_characters to ipa
        
        self.eye_acuity_wrapper = eye_acuity_wrapper
        
        '''
        Node context used
        e.g.
        Test
        node.context["characters_displayed"] = {"6/120" : ["a", "b"]}
        node.context["characters_score"] = {"6/120": 1}
        node.context["letters_spoken"] = False
        
        Progress
        node.context["second_eye"] = 0
        node.context["pinhole"] = 0
        node.context["va_score"] = {
            "left": "6/15 3 characters"
            "right": "6/15 1 character"
        }
        
        Signals
        node.context["process_text"] = "Text to process"
        node.context["audio_done"]: (DelayNode) When signaled, goes on to next node
        
        Reusable node combinations:
        Display -> Wait
        '''
        
        self.nodes = {
            "Default state": ProcessNode(), #Unsure if working
            "Listen for start": IONode(),
            "Check for start": DecisionNode(),
            "Play initial audio": ProcessNode(),
            "Wait for initial audio finish": DelayNode(),
            
            "wait_input": IONode(),
            "check_score": ProcessNode(),
            "able_to_read_all": DecisionNode(),
            "able_to_read_50": DecisionNode(),
            "display_node": ProcessNode(),
            "pinhole_node": ProcessNode(),
            "Reset node": ProcessNode(),
            
            "Display 6/120 letter": {},
            "Alert PSA": DecisionNode(),
            "Generic error": ProcessNode(), # Don't define next_node; it is dynamic
            "Display 6/60 and 6/45": {},
            
            # Only once when ending
            "Compute VA Score": ProcessNode(),
            "Print report": ProcessNode()
        }
        
        # Set up the reusable nodes, get them ready for copying
        self.nodes["wait_input"].set_signal_key("process_text")
        self.nodes["check_score"].callback = partial(self.calculate_score, self.nodes["check_score"])
        
        '''
        Callback methods
        '''
        
        def set_progress_callback(node, second_eye, pinhole):
            node.context["second_eye"] = 0
            node.context["pinhole"] = 0
            
        def check_for_start_callback(node):
            text = node.context["process_text"]
            text = text.lower()
            if "start" in text or "begin" in text:
                return True
            return False  
        
        def play_initial_instructions_process(node):
            if not node.context["second_eye"]:
                self.play_audio("/tts_recordings/stand_4_meters_away.mp3")
            else:
                self.play_audio("/tts_recordings/please_cover_other_eye.mp3")
        
        def generic_error(this: DecisionNode):
            self.play_audio("/tts_recordings/please_try_again.mp3")
        
        def pinhole_callback(this: FlowchartNode ):
            this.context["pinhole"] = 1
            print("Pinhole is now ", this.context["pinhole"])
            self.play_audio("/tts_recordings/pinhole.mp3")        
    
        def is_using_pinhole_decision(this: FlowchartNode):
            print("<Decision> Pinhole is now ", this.context["pinhole"])
            return this.context["pinhole"]
        
        def second_eye_tested_decision(this: FlowChartNode):
            return this.context["second_eye"]
        
        def able_to_read_all(node: ProcessNode, vam_size):
            if len(node.context["characters_displayed"][vam_size]) > node.context["characters_score"][vam_size]:
                print("Unable to read all of ", vam_size)
                return False
            print("Able to read all of ", vam_size)
            return True
        
        def able_to_read_50(node: ProcessNode, vam_size):
            if len(node.context["characters_displayed"][vam_size]) > node.context["characters_score"][vam_size]*2:
                print("Unable to read 50% of ", vam_size)
                return False
            print("Able to read 50% of ", vam_size)
            return True
        
        def any_letters_spoken_decision(node: DecisionNode):
            return node.context["letters_spoken"]

        def compute_va_score_process(node: ProcessNode):
            context = node.context
            vam_sizes = context["characters_displayed"].keys()
            
            failed_vam_size = ""
            for vam_size in vam_sizes:
                if not able_to_read_all(node, vam_size):
                    failed_vam_size = vam_size
                    break
            if failed_vam_size == "": failed_vam_size = vam_size
            score = context["characters_score"][failed_vam_size]
            max_score = len(context["characters_displayed"][failed_vam_size])
            
            if context["second_eye"]:
                context["va_score"]["right"] = vam_size + ": " + str(score) + " / " + str(max_score)
            else:
                #!!! Testing purposes
                context["second_eye"] = 1
                context["pinhole"] = 0
                context["va_score"] = {"left": vam_size + ": " + str(score) + " / " + str(max_score)}
                
            print(" Computer VA Score ")
            print(context["va_score"])
            
        def print_report_process(node: ProcessNode):
            context = node.context
            print("<PRINT REPORT> ", context["va_score"])
            report_text = "(Left eye) " + context["va_score"]["left"]
            if "right" in context["va_score"]: report_text += " | (Right eye) " + context["va_score"]["right"]
            self.display_text(report_text)
            
            # Clear report after printing
            if "right" in context["va_score"]:
                set_progress_callback(node, 0,0)
                del context["va_score"]
                
        '''
        Node generating functions
        '''        
        # Add wait and check blocks behind given node
        def add_wait_check(node) -> DecisionNode: 
            '''
            Return:
            
            DecisionNode: Use returnedNode.true_node to continue programme flow
            '''
            wait_input = copy.copy(self.nodes["wait_input"])
            check_score = copy.copy(self.nodes["check_score"])
            any_letters_spoken = DecisionNode()
            any_letters_spoken.callback = partial(any_letters_spoken_decision, any_letters_spoken)
            any_letters_spoken.false_node = wait_input
            node.next_node = wait_input
            wait_input.next_node = check_score
            check_score.next_node = any_letters_spoken

            return any_letters_spoken
        
        def generate_one_per_size(*vam):
            '''
            Generate nodes Display => Read out => Able to read? => Able to read? ...
            '''
            # Tuples to pass in as parameter into display_characters 
            display_tuples = []
            for i in vam:
                display_tuples.append((1,i))
            # Set up the display nodes
            display_node = copy.copy(self.nodes["display_node"])
            display_node.callback = partial(self.display_characters, display_node, *display_tuples)
            
            # Order it so node => display_node
            #node.next_node = display_node
            
            # curr_node is now the "latest" node, at "check_score"
            # node => display_node => wait_input => check_score
            curr_node = add_wait_check(display_node)
            
            return_dict = {
                "display": display_node,
                "wait": display_node.next_node,
                "calculate": display_node.next_node.next_node,
                "any_letters_spoken": display_node.next_node.next_node.next_node
            }
            # Generate validate nodes, per item in vam
            # node => display_node => wait_input => check_score => validate_6/120 => validate_6/60...
            for i in vam:
                validate_node = copy.copy(self.nodes["able_to_read_all"])
                validate_node.callback = partial(able_to_read_all, validate_node, i)
                curr_node.true_node = validate_node
                
                curr_node = validate_node
                return_dict["validate_"+i] = validate_node
            '''
            {
                "display": display_node,
                "wait": display_node.next_node,
                "calculate": display_node.next_node.next_node,
                "any_letters_spoken": display_node.next_node.next_node.next_node,
                "validate_6/120": display_node.next_node.next_node.next_node.next_node,
                "validate_6/60": display_node.next_node.next_node.next_node.next_node.next_node
                ...
            }
            '''
            return return_dict
            #print(*generate_display_tuples)     
        
        # Generate "Use pinhole" node
        def generate_pinhole_node(next_node: FlowChartNode = None) -> FlowChartNode:            
            pinhole_node = copy.copy(self.nodes["pinhole_node"])
            pinhole_node.callback = partial(pinhole_callback, pinhole_node)
            pinhole_node.next_node = next_node
            return pinhole_node

        def generate_multiple_one_size(vam_size, num_of_char):
            '''
            Note: Will need to manually assign: 
            
                "validate_{vam_size}" true node
                
            --- 
            
            Return
            
            {
                "display": display_node,
                "wait": display_node.next_node,
                "calculate": display_node.next_node.next_node
                "validate_{vam_size}": display_node.next_node.next_node.next_node
            }
            '''
            # <!> Need result screen node
            
            # Set up the display nodes
            display_node = ProcessNode() #copy.copy(self.nodes["display_node"])
            display_node.callback = partial(self.display_characters, display_node, (num_of_char, vam_size))
            
            # curr_node is now the "latest" node, at "any_letters_spoken"
            # node => display_node => wait_input => check_score => any_letters_spoken
            curr_node = add_wait_check(display_node)
            
            # Generate validate node (able to read >50%?)
            score_validate = copy.copy(self.nodes["able_to_read_50"])
            score_validate.callback = partial(able_to_read_50, score_validate, vam_size)
            
            curr_node.true_node = score_validate
            curr_node = score_validate
            
            is_using_pinhole_node: DecisionNode = DecisionNode()
            is_using_pinhole_node.callback = partial(is_using_pinhole_decision, is_using_pinhole_node)
            is_using_pinhole_node.false_node = generate_pinhole_node(display_node.next_node)
            is_using_pinhole_node.true_node = self.nodes["Compute VA Score"]
            score_validate.false_node = is_using_pinhole_node
            
            return_dict = {
                "display": display_node,
                "wait": display_node.next_node,
                "calculate": display_node.next_node.next_node,
                "any_letters_spoken": display_node.next_node.next_node.next_node,
                "validate_" + vam_size: score_validate,
                "is_using_pinhole_node": is_using_pinhole_node
            }
            return return_dict
        
        
        self.ge = self.nodes["Generic error"]
        self.ge.callback = partial(generic_error, self.ge)
        # Reset node
        reset_n = self.nodes["Reset node"]
        reset_n.callback = partial(set_progress_callback, reset_n, 0, 0)
        reset_n.next_node = self.nodes["Default state"]
        self.current_node = reset_n
        
        if 'wait until "start" or "begin"':
            # Default state
            default_n = self.nodes["Default state"]
            #default_n.callback = partial(self.remove_letters) #partial(self.display_instructions)
            default_n.next_node = self.nodes["Listen for start"]
            
            # Wait for start Command
            self.nodes["Listen for start"].set_signal_key("process_text")
            self.nodes["Listen for start"].next_node = self.nodes["Check for start"]
            
            # Did the person say the Start command?
            cfs = self.nodes["Check for start"]
            cfs.callback = partial(check_for_start_callback, cfs)
            cfs.false_node = self.nodes["Default state"]
            cfs.true_node = self.nodes["Play initial audio"]
            
            # Play instruction audio
            pia = self.nodes["Play initial audio"]
            pia.callback = partial(play_initial_instructions_process, pia)
            pia.next_node = self.nodes["Wait for initial audio finish"]
        
        if "Compute VA Score":
            compute_va_score_node = self.nodes["Compute VA Score"]
            compute_va_score_node.callback = partial(compute_va_score_process, compute_va_score_node)
        
        if "Print report":
            print_report_node = self.nodes["Print report"]
            print_report_node.callback = partial(print_report_process, print_report_node)
            #print_report_node.next_node = self.nodes["Reset node"]
            print_report_node.next_node = self.nodes["Default state"]
            
            
            # !!! For testing only
            compute_va_score_node.next_node = print_report_node
            
        
        # Block until audio is done
        wiaf = self.nodes["Wait for initial audio finish"]
        wiaf.set_signal_key("audio_done")
        #wiaf.next_node = self.nodes["Display 6/120 letter"]
        
        if 'Display 6/120 letter':
            # <!> To do: Alert PSA
            
            # display_node => wait_input => check_score => validate_6/120 => validate_6/60...
            nodes = generate_one_per_size("6/120")
            
            # link wiaf => display_node
            wiaf.next_node = nodes["display"]
            
            # => validate_6/120 => (if error) => generic_error
            nodes["validate_6/120"].false_node = copy.copy(self.ge)
            # => generic_error => wait
            nodes["validate_6/120"].false_node.next_node = nodes["wait"]
            
            self.nodes["Display 6/120 letter"] = nodes
        
        if "Display 6/60 and 6/45":
            v6120 = self.nodes["Display 6/120 letter"]["validate_6/120"]
            
            # Create nodes display => wait => calculate => validate
            nodes = generate_one_per_size("6/60", "6/45")
            print(nodes)
            self.nodes["Display 6/60 and 6/45"] = nodes
            
            # Link previous node to current nodes
            #   link v6120 => display
            v6120.true_node = nodes["display"]  
            
            precise_nodes = generate_multiple_one_size("6/60", 3)
            nodes["validate_6/60"].false_node = generate_pinhole_node(precise_nodes["display"])
            
            nodes["validate_6/45"].false_node = precise_nodes["display"]
            
            # Loop at 6/60 and 6/45 for demo purposes
            nodes["validate_6/45"].true_node = nodes["display"]
            precise_nodes["validate_6/60"].true_node = precise_nodes["display"]
        
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
            #node.context["characters_displayed"] = {}
            self.eye_acuity_wrapper.run_javascript(javascript)
    
    # Show letters on the screen
    def display_characters(self, node, *chara_tuples):
        self.remove_letters()
        '''
        (num_of_characters, vam_size)
        <!> Random positioning of these characters, no overlap
        '''
        node.context["characters_displayed"] = {}
        for i in chara_tuples:
            num_of_characters = i[0]
            vam_size = i[1]
            font_size = self.vam_to_font_size[vam_size]
            # <!> Generate characters, based on num_of_characters
            print("Generate ", num_of_characters, " characters")
            
            chosen_ones = []
            chosen_ones = random.sample(self.generable_characters, num_of_characters)
            
            node.context["characters_displayed"][vam_size] = chosen_ones
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
    
    # Calculate score
    def calculate_score(self, node):
        # <!> Order currently not maintained
        context = node.context
        
        # Reset score
        context["characters_score"] = {}
        
        user_input = context["process_text"]
        
        user_input = user_input.replace("-"," ")
        
        # Bandaid for issue: "Letters stuck together may be considered as word, hence ipa conversion fails"
        total_char_length = 0
        # Calculate total length of characters
        for vam_size, characters in context["characters_displayed"].items():
            total_char_length+=len(characters)
        if len(''.join(e for e in user_input if e.isalnum())) <= total_char_length:
            print("User input is shorter:", user_input, len(user_input))
            user_input = list(user_input)
            print(user_input)
        else:
            print("User input is not shorter:", user_input, len(user_input))
            user_input = user_input.split(" ")
    
        ipa_user_input = []
        for i in user_input:
            if p.convert(i) in self.ipa_letters:
                ipa_user_input.append(p.convert(i))
        
        print("IPA of user input is: ", ipa_user_input)
        # Determine if any letters is spoken at all
        if (len(ipa_user_input) == 0): 
            context["letters_spoken"] = False
            return False
        else:
            context["letters_spoken"] = True
            
        # Tabulate score for each characters
        for vam_size,characters in context["characters_displayed"].items():
            context["characters_score"][vam_size] = 0
            for cd in characters:
                # Get the ipa(s) of the displayed character
                ipas = self.character_ipa_map[cd]
                for ipa in ipas:
                    if ipa in ipa_user_input:
                        # If user said character, score increases
                        context["characters_score"][vam_size] += 1
                        ipa_user_input.remove(ipa)
                        break
        
        print("Context is ", context)
        for vam_size, score in context["characters_score"].items():
            if len(context["characters_displayed"][vam_size]) > score:
                print("<Check characters> False")
                return False
        return True
        
    def display_text(self, text):
        self.remove_letters()
        javascript = f"""
            // Get the <p> element under the "letters" class
            var lettersParagraph = document.querySelector(".letters");

            var para = document.createElement('p');
            // Define the text you want to set
            var newText = "{text}";

            // Set the text content of the <p> element
            para.textContent = newText;
            
            para.style.fontSize = "0.3cm";
            lettersParagraph.appendChild(para);
            """
            
            # <!> Call run_javascript method of eye_acuity_wrapper
        self.eye_acuity_wrapper.run_javascript(javascript)
        
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

    def play_audio(self, audio_file_path):
        self.eye_acuity_wrapper.play_audio(audio_file_path)

if __name__ == "__main__":
    jr = EyeAcuityWrapper()
    eat = EyeAcuityTest(jr)
    eat.run()
    while eat.current_node is not None:
        print("Current node:", eat.current_node)
        #s_key = input("Enter signal key: ")
        s_data = input("Enter signal data: ")
        eat.signal("process_text", s_data)
        eat.signal("audio_done", s_data)