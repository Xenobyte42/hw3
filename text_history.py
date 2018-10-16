"""
This module implements the storage of versions of the text
"""

from abc import abstractmethod, ABC


class TextHistory:
    """
    The class stores the text and the history of its changes
    """

    def __init__(self):
        self._text = ""
        self._version = 0
        self.__actions_list = []

    @property
    def text(self):
        """
        Text getter
        """
        return self._text

    @property
    def version(self):
        """
        Version getter
        """
        return self._version

    def insert(self, txt, pos=None):
        """
        The method adds text at the specified position
        """

        if pos is None:
            pos = len(self._text)

        act = InsertAction(pos, txt, self._version, self._version + 1)
        self.action(act)
        return self._version

    def replace(self, txt, pos=None):
        """
        The method replaces the text at the specified position
        """

        if pos is None:
            pos = len(self._text)

        act = ReplaceAction(pos, txt, self._version, self._version + 1)
        self.action(act)
        return self._version

    def delete(self, pos, length):
        """
        The method deletes the text of the specified
        length at the specified position
        """

        act = DeleteAction(pos, length, self._version, self._version + 1)
        self.action(act)
        return self._version

    def action(self, action):
        """
        The method applies the specified action to the stored text
        """

        if self._version != action.from_version:
            raise ValueError("incopatible versions.")

        self._text = action.apply(self._text)
        self._version = action.to_version
        self.__actions_list.append(action)
        return self._version

    @staticmethod
    def try_merge_delete(action, optimize_act_list):
        """
        Optimizes delete actions
        """

        pre_action = optimize_act_list[-1]
        if pre_action.pos == action.pos:
            action = DeleteAction(action.pos,
                                  pre_action.length + action.length,
                                  pre_action.from_version, action.to_version)
            optimize_act_list.pop()
        optimize_act_list.append(action)

    @staticmethod
    def try_merge_insert(action, optimize_act_list):
        """
        Optimizes insert actions
        """

        pre_action = optimize_act_list[-1]
        if action.pos == (pre_action.pos + len(pre_action.text)):
            action = InsertAction(pre_action.pos,
                                  pre_action.text + action.text,
                                  pre_action.from_version, action.to_version)
            optimize_act_list.pop()
        optimize_act_list.append(action)

    @staticmethod
    def optimize(act_list):
        """
        Optimizes the list of actions
        """

        optimize_act_list = []
        for action in act_list:
            if optimize_act_list:
                if isinstance(optimize_act_list[-1], type(action)):
                    if isinstance(action, InsertAction):
                        TextHistory.try_merge_insert(action, optimize_act_list)
                    elif isinstance(action, DeleteAction):
                        TextHistory.try_merge_delete(action, optimize_act_list)
                    else:
                        optimize_act_list.append(action)
                else:
                    optimize_act_list.append(action)
            else:
                optimize_act_list.append(action)

        return optimize_act_list

    def get_actions(self, from_version=None, to_version=None):
        """
        The method returns a list of actions in the version range
        """

        if from_version is None:
            from_version = 0
        if to_version is None:
            to_version = self._version
        if from_version > self._version or to_version > self._version:
            raise ValueError("incopatible versions.")
        elif from_version > to_version:
            raise ValueError("incopatible versions.")
        elif from_version < 0 or to_version < 0:
            raise ValueError("incopatible versions.")

        act_list = []
        for action in self.__actions_list:
            if from_version <= action.from_version < to_version:
                act_list.append(action)
        act_list = self.optimize(act_list)
        return act_list


class Action(ABC):
    """
    Action base class
    """

    def __init__(self, pos, from_version, to_version):
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version

    @abstractmethod
    def apply(self, text):
        """
        Will be override later
        """
        pass


class InsertAction(Action):
    """
    The class which implements the insertion in the text
    """

    def __init__(self, pos, text, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    def __str__(self):
        return "insert({}, pos={}, \
                ver1={}, ver2={})".format(self.text, self.pos,
                                          self.from_version, self.to_version)

    def apply(self, text):
        if self.pos > len(text) or self.pos < 0:
            raise ValueError("incorrect pos in InsertAction.")

        text = text[:self.pos] + self.text + text[self.pos:]
        return text


class ReplaceAction(Action):
    """
    The class that implements substitution in the text
    """

    def __init__(self, pos, text, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.text = text

    def __str__(self):
        return "replace({}, pos={}, \
                ver1={}, ver2={})".format(self.text, self.pos,
                                          self.from_version, self.to_version)

    def apply(self, text):
        if self.pos > len(text) or self.pos < 0:
            raise ValueError("incorrect pos in ReplaceAction")

        end_idx = self.pos + len(self.text)
        if end_idx >= len(text):
            text = text[:self.pos] + self.text
        else:
            text = text[:self.pos] + self.text + text[end_idx:]
        return text


class DeleteAction(Action):
    """
    The class that implements removal from the text
    """

    def __init__(self, pos, length, from_version, to_version):
        super().__init__(pos, from_version, to_version)
        self.length = length

    def __str__(self):
        return "delete(pos={}, length={}, \
                ver1={}, ver2={})".format(self.pos, self.length,
                                          self.from_version, self.to_version)

    def apply(self, text):
        if self.pos + self.length > len(text) or self.pos < 0:
            raise ValueError("incorrect pos in DeleteAction.")

        text = text[:self.pos] + text[self.pos + self.length:]
        return text


if __name__ == "__main__":
    pass
