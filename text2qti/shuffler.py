import random
import re

NO_SHUFFLE_RE = r'^##[Nn]o[_\s]?shuffle\s*\n'

class Shuffler:
    def __init__(self):
        pass

    def shuffle(self, text):
        ''' sdf '''        
        # Example usage
        # with open('testqti.txt', 'r', encoding='utf-8') as f:
        #    content = f.read()

        # 
        for line in text:
            if line.strip():  # Found first non-blank line
                break
        # Split questions by number pattern (e.g., "1. ")
        if re.match(NO_SHUFFLE_RE, text, flags=re.IGNORECASE):
            return re.sub(NO_SHUFFLE_RE, "", text, re.IGNORECASE)
        question_blocks = re.split(r'\n(?=\d+\.\s|#no_shuffle)', text)
        question_blocks = self.merge_no_shuffle_blocks(question_blocks)
        shuffled_blocks = [self.shuffle_mc_question(block) for block in question_blocks]
        shuffled_quiz = '\n\n'.join(shuffled_blocks)
        return shuffled_quiz
        #with open('shuffled_testqti.txt', 'w', encoding='utf-8') as f:
        #    f.write(shuffled_quiz)

        # print("Shuffled quiz saved as 'shuffled_testqti.txt'")

    def shuffle_mc_question(self, question_block):
        '''  the main processor for shuffling '''

        lines = question_block.strip().split('\n')
        if re.search(r'#no[_\s]?shuffle', question_block, re.IGNORECASE):
            return  '\n'.join(lines[1:])  # Skip shuffling this block and remove tag
        question_text = []
        choices = []
        correct_choice = None

        # Separate question and choices
        for line in lines:
            if re.match(r'^\*?[a-eA-E]\)', line.strip()):
                choices.append(line.strip())
            else:
                question_text.append(line)

        # Check for "all of" or "none of" in any choice
        if any("all of" in choice.lower() or "none of" in choice.lower() for choice in choices):
            return '\n'.join(question_text + choices)  # Skip shuffling
        # skip two-choice "a) true  and b) false"
        if len(choices) == 2 and re.search(r'a\)\s+true', choices[0], flags=re.IGNORECASE) and re.search(r'b\)\s+false', choices[1], flags=re.IGNORECASE):
            return '\n'.join(question_text + choices)  # Skip shuffling


        # Identify correct answer
        correct_index = None
        for i, choice in enumerate(choices):
            if choice.startswith('*'):
                correct_index = i
                correct_choice = choice[1:].strip()  # Remove asterisk
                break

        if correct_index is None:
            return '\n'.join(question_text + choices)  # No correct answer marked

        # Remove correct choice and shuffle others
        other_choices = choices[:correct_index] + choices[correct_index+1:]
        other_choices = [c.lstrip('*').strip() for c in other_choices]
        random.shuffle(other_choices)

        # Insert correct choice at random position
        new_index = random.randint(0, len(choices)-1)
        shuffled_choices = other_choices[:new_index] + [correct_choice] + other_choices[new_index:]

        # Reassign choice letters and mark correct one
        choice_letters = ['a)', 'b)', 'c)', 'd)', 'e)']
        formatted_choices = []
        #     for i, choice in enumerate(shuffled_choices):
        #    prefix = f"*{choice_letters[i]}" if i == new_index else choice_letters[i]
        #    formatted_choices.append(f"{prefix} {choice}")
        for i, choice in enumerate(shuffled_choices):
        # Remove any existing label like "a) ", "B) ", etc.
            clean_text = re.sub(r'^\*?[a-eA-E]\)\s*', '', choice)
            prefix = f"*{choice_letters[i]}" if i == new_index else choice_letters[i]
            formatted_choices.append(f"{prefix} {clean_text}")

        return '\n'.join(question_text + formatted_choices)


    def merge_no_shuffle_blocks(self, blocks):
        ''' skip blocks tagged '#no_shuffle' '''
        merged = []
        # skip_next = False

        i = 0
        while i < len(blocks):
            block = blocks[i].strip()

            if block.startswith("#no_shuffle"):
                # Merge with next block if it exists
                if block == "#no_shuffle":
                    if i + 1 < len(blocks):
                        merged.append("#no_shuffle\n" + blocks[i + 1].strip())
                        i += 2  # Skip the next block since it's merged
                    else:
                        merged.append(block)  # Edge case: #no_shuffle is last
                        i += 1
                else:
                    raise ValueError("A question block starting with '#.' was expected"
                                    "after a '#no_shuffle' directive")
            else:
                merged.append(block)
                i += 1
        return merged
