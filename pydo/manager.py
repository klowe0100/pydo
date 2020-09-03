"""
Module to store the main class of pydo

Classes:
    TaskManager: Class to manipulate the tasks data
"""
import datetime
import logging

from pydo.model import RecurrentTask, Tag, Task

log = logging.getLogger(__name__)


class TableManager:
    """
    Abstract Class to manipulate a database table data.

    Arguments:
        session (session object): Database session
        table_model (Sqlalchemy model): Table model

    Internal methods:
        _add: Method to create a new table item
        _get: Retrieve the table element identified by id.
        _get_attributes: Method to extract the object attributes to a
            dictionary.
        _update: Method to update an existing table item

    Public attributes:
        session (session object): Database session
    """

    def __init__(self, session, table_model):
        self.model = table_model
        self.session = session

    def _add(self, id, object_values):
        """
        Method to create a new table item

        Arguments:
            id (str): object identifier
            object_values (dict): Dictionary with the column identifier
                as keys.
        """

        obj = self.model(id=id)

        for attribute_key, attribute_value in object_values.items():
            setattr(obj, attribute_key, attribute_value)

        try:
            title = object_values["title"]
        except KeyError:
            title = None

        self.session.add(obj)
        self.session.commit()
        log.debug("Added {} {}: {}".format(self.model.__name__.lower(), id, title,))

    def _get(self, id):
        """
        Return the table element identified by id.

        Arguments:
            id (str): Table element identifier

        Returns:
            table element (obj): Sqlalchemy element of the table.
            raises: ValueError if element is not found
        """

        table_element = self.session.query(self.model).get(id)

        if table_element is None:
            raise ValueError("The element {} does not exist".format(id))
        else:
            return table_element

    def _update(self, id, object_values=None):
        """
        Method to update an existing table item

        Arguments:
            id (str): object identifier
            object_values (dict): Dictionary with the column identifier
                as keys.
        """

        table_element = self.session.query(self.model).get(id)

        if table_element is None:
            raise ValueError("The element {} does not exist".format(id))
        else:
            if object_values is not None:
                for attribute_key, attribute_value in object_values.items():
                    setattr(table_element, attribute_key, attribute_value)

            self.session.commit()
            log.debug("Modified {}: {}".format(id, object_values,))


class TaskManager(TableManager):
    """
    Class to manipulate the tasks data.

    Arguments:
        session (session object): Database session

    Public methods:
        add: Creates a new task.
        complete: Completes a task.
        delete: Deletes a task.
        freeze: Freezes a task.
        modify: Modifies a task.
        modify_parent: Modifies the parent task.
        unfreeze: Unfreezes a task.

    Internal methods:
        _add: Parent method to add table elements.
        _close: Closes a task.
        _close_children_hook: Method to call different hooks for each parent
            type once a children has been closed.
        _create_next_fulid: Method to create the next task's fulid.
        _generate_children_attributes: Method to generate the next children
            task attributes.
        _get_fulid: Method to get the task's fulid if necessary.
        _parse_arguments: Parse a Taskwarrior like add query into task
            attributes.
        _parse_attribute: Parse a Taskwarrior like add argument into a task
            attribute.
        _rm_tags: Method to delete tags from the Task attributes.
        _set: Method to set the task's attributes and get its fulid.
        _set_agile: Method to set the agile attribute.
        _set_project: Method to set the project attribute.
        _set_tags: Method to set the tags attribute.
        _spawn_next_recurring: Method to spawn the next recurring children
            task.
        _spawn_next_repeating: Method to spawn the next repeating children
            task.
        _unfreeze_parent_hook: Method to call the different hooks for each
            parent type once it's unfrozen
        _update: Parent method to update table elements.

    Public attributes:
        date (DateManager): DateManager object.
        fulid (fulid object): Fulid manager and generator object.
        session (session object): Database session
        recurrence (TableManager): RecurrenceTask manager
    """

    def __init__(self, session):
        super().__init__(session, Task)
        self.recurrence = TableManager(session, RecurrentTask)

    # def _get_fulid(self, id, state="open"):
    #      == repo.short_id_to_id

    def _generate_children_attributes(self, parent_task):
        """
        Method to generate the next children task attributes.

        Arguments:
            parent_task (RecurrentTask):

        Returns:
            child_attributes (dict): Children attributes
        """

        child_attributes = self._get_attributes(parent_task)
        child_attributes.pop("recurrence")
        child_attributes.pop("recurrence_type")
        child_attributes["id"] = self._create_next_fulid().str
        child_attributes["parent_id"] = parent_task.id
        child_attributes["type"] = "task"

        return child_attributes

    def _rm_tags(self, task_attributes, tags_rm=[]):
        """
        Method to delete tags from the Task attributes.

        Arguments:
            task_attributes (dict): Dictionary with the attributes of the task.
            tags_rm (list): List of tag ids to remove.
        """
        for tag_id in tags_rm:
            tag = self.session.query(Tag).get(tag_id)
            if tag is None:
                raise ValueError("The tag doesn't exist")
            task_attributes["tags"].remove(tag)

    def _set(self, id=None, project_id=None, tags=[], tags_rm=[], agile=None, **kwargs):
        """
        Method to set the task's attributes and get its fulid.

        Arguments:
            id (str): Ulid of the task if it already exists.
            project_id (str): Project id.
            tags (list): List of tag ids.
            tags_rm (list): List of tag ids to remove.
            agile (str): Task agile state.
            **kwargs: (object) Other attributes (key: value).

        Returns:
            fulid (str): fulid that matches the sulid.
            task_attributes (dict): Dictionary with the attributes of the task.
        """
        fulid = None
        task_attributes = {}

        if id is not None:
            fulid = self._get_fulid(id)

            task = self.session.query(Task).get(fulid)
            task_attributes["tags"] = task.tags

            self._rm_tags(task_attributes, tags_rm)

        self._set_tags(task_attributes, tags)

        if agile == "":
            task_attributes["agile"] = None
        else:
            self._set_agile(task_attributes, agile)

        for key, value in kwargs.items():
            if value == "":
                value = None
            task_attributes[key] = value

        return fulid, task_attributes

    def modify(self, id, project_id=None, tags=[], tags_rm=[], agile=None, **kwargs):
        """
        Use parent method to modify an existing task.

        Arguments:
            project_id (str): Project id.
            tags (list): List of tag ids.
            tags_rm (list): List of tag ids to remove.
            agile (str): Task agile state.
            **kwargs: (object) Other attributes (key: value).
        """
        fulid, task_attributes = self._set(
            id, project_id, tags, tags_rm, agile, **kwargs
        )

        self._update(
            fulid, task_attributes,
        )

    def modify_parent(self, id, **kwargs):
        """
        Use parent method to modify the parent of an existing task.

        Arguments:
            id (str): child id.
            **kwargs: (object) Other attributes (key: value).
        """

        fulid = self._get_fulid(id)
        child_task = self.session.query(Task).get(fulid)

        if child_task.parent_id is None:
            log.error("Task {} doesn't have a parent task".format(child_task.id))
        else:
            self.modify(child_task.parent_id, **kwargs)

    def _close_children_hook(self, task):
        """
        Method to call different hooks for each parent type once a children
        has been closed

        Arguments:
            task (Task): Children closed task
        """
        if task.parent.state != "frozen":
            if task.parent.recurrence_type == "recurring":
                self._spawn_next_recurring(task.parent)
            elif task.parent.recurrence_type == "repeating":
                self._spawn_next_repeating(task.parent)

    def delete(self, id, parent=False):
        """
        Method to delete a task

        Arguments:
            id (str): Ulid of the task
            parent (bool): Also delete parent task (False by default)
        """

        self._close(id, "deleted", parent)

    def freeze(self, id, parent=False):
        """
        Method to freeze a task.

        Arguments:
            id (str): Ulid of the task.
            parent (bool): Freeze the parent task instead(False by default).
        """

        fulid = self._get_fulid(id)
        task = self.session.query(Task).get(fulid)

        if parent and task.parent is not None:
            task.parent.state = "frozen"
        else:
            task.state = "frozen"
        self.session.commit()

    def unfreeze(self, id, parent=False):
        """
        Method to unfreeze a task.

        Arguments:
            id (str): Ulid of the task
            parent (bool): Unfreeze the parent task instead(False by default).
        """

        fulid = self._get_fulid(id, "frozen")
        task = self.session.query(Task).get(fulid)
        if parent and task.parent is not None:
            task.parent.state = "open"
        else:
            task.state = "open"

        self.session.commit()

        if task.type != "task":
            self._unfreeze_parent_hook(task)

    def _unfreeze_parent_hook(self, task):
        """
        Method to call different hooks for each parent type once it's unfrozen

        Arguments:
            task (Task): Parent unfrozen task
        """

        children_states = [children.state for children in task.children]

        if "open" not in children_states:
            if task.recurrence_type == "recurring":
                self._spawn_next_recurring(task)
            elif task.recurrence_type == "repeating":
                self._spawn_next_repeating(task)
