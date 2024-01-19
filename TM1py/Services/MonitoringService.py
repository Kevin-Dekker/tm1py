# -*- coding: utf-8 -*-
from typing import List
from warnings import warn
from requests import Response

from TM1py import ThreadService
from TM1py.Objects.User import User
from TM1py.Services.ObjectService import ObjectService
from TM1py.Services.RestService import RestService
from TM1py.Services.UserService import UserService
from TM1py.Utils import format_url, case_and_space_insensitive_equals, require_admin, deprecated_in_version


class MonitoringService(ObjectService):
    """ Service to Query and Cancel Threads in TM1
    
    """

    def __init__(self, rest: RestService):
        super().__init__(rest)
        warn("Monitoring Service will be moved to a new location in a future version", DeprecationWarning, 2)
        self.users = UserService(rest)
        self.threads = ThreadService(rest)

    def get_threads(self, **kwargs) -> List:
        """ Return a dict of the currently running threads from the TM1 Server

            :return:
                dict: the response
        """
        return self.threads.get()

    def get_active_threads(self, **kwargs):
        """Return a list of non-idle threads from the TM1 Server

            :return:
                list: TM1 threads as dict
        """
        return self.threads.get_active()

    def cancel_thread(self, thread_id: int, **kwargs) -> Response:
        """ Kill a running thread
        
        :param thread_id: 
        :return: 
        """
        return self.threads.cancel(thread_id)

    def cancel_all_running_threads(self, **kwargs) -> list:
        return self.threads.cancel_all_running()

    def get_active_users(self, **kwargs) -> List[User]:
        """ Get the activate users in TM1

        :return: List of TM1py.User instances
        """
        return self.users.get_active()

    def user_is_active(self, user_name: str, **kwargs) -> bool:
        """ Check if user is currently active in TM1

        :param user_name:
        :return: Boolean
        """
        return self.users.is_active(user_name)

    def disconnect_user(self, user_name: str, **kwargs) -> Response:
        """ Disconnect User
        
        :param user_name: 
        :return: 
        """
        return self.users.is_active(user_name)

    def get_active_session_threads(self, exclude_idle: bool = True, **kwargs):
        url = "/ActiveSession/Threads?$filter=Function ne 'GET /ActiveSession/Threads'"
        if exclude_idle:
            url += " and State ne 'Idle'"

        response = self._rest.GET(url, **kwargs)
        return response.json()['value']

    def get_sessions(self, include_user: bool = True, include_threads: bool = True, **kwargs) -> List:
        url = "/Sessions"
        if include_user or include_threads:
            expands = list()
            if include_user:
                expands.append("User")
            if include_threads:
                expands.append("Threads")
            url += "?$expand=" + ",".join(expands)

        response = self._rest.GET(url, **kwargs)
        return response.json()["value"]

    @require_admin
    def disconnect_all_users(self, **kwargs) -> list:
        return self.users.disconnect_all

    def close_session(self, session_id, **kwargs) -> Response:
        url = format_url(f"/Sessions('{session_id}')/tm1.Close")
        return self._rest.POST(url, **kwargs)

    @require_admin
    def close_all_sessions(self, **kwargs) -> list:
        current_user = self.get_current_user(**kwargs)
        sessions = self.get_sessions(**kwargs)
        closed_sessions = list()
        for session in sessions:
            if "User" not in session:
                continue
            if session["User"] is None:
                continue
            if "Name" not in session["User"]:
                continue
            if case_and_space_insensitive_equals(current_user.name, session["User"]["Name"]):
                continue
            self.close_session(session['ID'], **kwargs)
            closed_sessions.append(session)
        return closed_sessions

    def get_current_user(self, **kwargs):
        return self.users.get_current()
