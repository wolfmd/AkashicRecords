
class StateService(object):

    nlp_vis_option_part_of_speech = "part_of_speech"
    nlp_vis_option_subject_verb_object = "subject_verb_object"
    nlp_vis_option_entities = "entities"
    nlp_vis_option_sentiment = "sentiment"


    state = {
        "nlp_visualization_options": {
            "part_of_speech": False,
            "subject_verb_object": False,
            "entities": False,
            "sentiment": False
        }
    }





    def __init__(self, **kwargs):
        self.__dict__ = {}




    def _reset_options_dict(self, options_dict):
        return dict.fromkeys(options_dict, False)




    def nlp_vis_option_selected(self, selected_option):
        self.state['nlp_visualization_options'] = self._reset_options_dict(self.state['nlp_visualization_options'])
        self.state['nlp_visualization_options'][selected_option] = True

