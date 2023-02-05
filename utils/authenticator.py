#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from utils.manager_base import ManagerBase
import requests as req
import logging

logger = logging.getLogger(__name__)


class Authenticator(ManagerBase):
    def __init__(self, backend_url: str):
        self.url = backend_url
        self.csrf = req.get(self.url + "/auth/csrf", verify=False)
        self.pkey = req.get(self.url + "/auth/pkey", verify=False)
        self.pem = req.get(self.url + "/auth/pem", verify=False)
        self.csrf_delivery = req.get(self.url + "/delivery/csrf", verify=False)
        self.jwt_cookie = None

    def login(self, username: str, password: str) -> bool:
        """Login current box to the backend

        Args:
            username (str): user name to login
            password (str): password w.r.t. to the user

        Returns:
            bool: login success
        """
        r = req.post(
            self.url + "/auth/jwe/box",
            json={"username": username, "password": password},
            cookies=self.csrf.cookies,
            headers=self.csrf.cookies.get_dict(),
            verify=False
        )
        self.jwt_cookie = r.cookies
        logger.info("Login status code: {}, text {}.".format(r.status_code, r.text))
        return r.status_code == 200

    def auth(self, username: str, token: str) -> bool:
        """Authenticate, returns True if user has one or more packet to pick up

        Args:
            username (str): user name
            token (str): user token, read from RFID

        Returns:
            bool: result
        """
        r = req.get(
            self.url + "/order/list/{}?token={}".format(username, token),
            cookies=self.jwt_cookie,
            verify=False
        )
        logger.info("Auth status code: {}, text {}.".format(r.status_code, r.text))
        if r.status_code != 200:
            return False
        return len(eval(r.text)) > 0

    def update_box(self, username: str, token: str) -> bool:
        """Updates the box status when the customer/deliver successfully opened and closed the box

        Args:
            username (str): user name
            token (str): user token, read from RFID

        Returns:
            bool: True if the update is successful
        """
        if self.jwt_cookie is None:
            logger.error("No jwt cookie cached, unable to access backend!!")
            return False
        fake_cookie = self.jwt_cookie.get_dict()
        fake_cookie.update(self.csrf_delivery.cookies.get_dict())
        r = req.put(
            self.url + "/order/change-status/{}/{}".format(username, token),
            cookies=fake_cookie,
            headers=self.csrf_delivery.cookies.get_dict(),
            verify=False
        )
        logger.info(
            "Box update status code: {}, text {}.".format(r.status_code, r.text)
        )
        return r.status_code == 200
