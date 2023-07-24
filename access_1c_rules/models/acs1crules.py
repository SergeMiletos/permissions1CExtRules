# -*- coding: utf-8 -*-

from odoo import models, fields
from datetime import datetime, timedelta
import re

class Usr1CRules(models.Model):
    _name = 'acs1crules.usr1crules'
    _description = 'External user permissions checking for 1C:Enterprise'

    name = fields.Char(string="Rule name")
    objectType = fields.Selection([("DocProductsPurchaseOrder", "Purchase order"), ("DocProductsSaleOrder", "Sales order"),
                                   ("DocIncomeCashOrder", "Income cash order"), ("DocOutgoingCashOrder","Outgoing cash order"),
                                   ("DocWriteOffOrPostingItems","Write off or Posting Items (in stock)"), ("DocStockMoveItems","Move Items (in stock)"),
                                   ("DocInvoice","Invoice recieved"), ("DocCustomerReturn","Customer's return"),
                                   ("DocLandedCosts","Additional (landed) costs income"), ("DocOtherCosts","Other costs"), 
                                   ("DocPowerOfAttorney","Power of attorney"), ("DocCustomersOrder","Customer's order"), 
                                   ("DocOrderToSupplier","Order to supplier"), ("RefProducts", "Products")], string="Controlled object in the 1C")

    ruleNumValue = fields.Integer(string="Value of the rule (number)")
    ruleStrValue = fields.Char(string="Value of the rule (string)")
    access1CGroup_ids = fields.Many2many('acs1crules.users1c_groups', string='Access groups')
    checkVariant = fields.Selection(selection=[("backDatedEditing", "Back date editing"),("writePermission","Write access permission")], string="Check variant", default="backDatedEditing")
    ruleType = fields.Selection(selection=[("ruleAllow","Rule allows access"),("ruleDeny","Rule denies access")],string="Rule type",default="ruleDeny")

    # Starting from 1
    rulePriority = fields.Integer(string="Priority level", default=1)
    rules_total = fields.Integer(compute='rules_count',string='Rules total')

    def rules_count(self):
        for record in self:
            record.rules_total = self.search_count([])

    """
    Returns False, if action denied, otherwise returns True
    obj_date_iso format: 'YYYY-MM-DD'
    """
    def _check_rule(self, objectType, user_name, objDate_iso, stage, *args):
#        import pudb; pudb.set_trace()
        user1c_id = self.env['acs1crules.users1c'].search([('name','ilike',user_name)])
        objDate = datetime.fromisoformat(objDate_iso)

        # Here and further I consider testResult True, if the rule fulfills the condition
        checksResult = [{"currentPriority":0, "testResult":False, "testType":"ruleDeny"}] # Allow by default

        if user1c_id:
            for single_rec in user1c_id:
                user_group_id = self.env['acs1crules.users1c_groups'].search([('users1c_ids', 'in', single_rec.id)])
                # User, that does not have group assign, has no permissions at all
                if not user_group_id:
                    checksResult.append({"currentPriority":1, "testResult":True, "testType":"ruleDeny"})

                for single_group in user_group_id:
                    if stage=="write":

                        rules = self.env['acs1crules.usr1crules'].search(["&",('access1CGroup_ids','in',single_group.id),('objectType','ilike',objectType)])

                        for single_rule in rules: # Deny rules

                            if single_rule.ruleType == "ruleDeny":
                                testResult = False
                                if not len(args):
                                    if single_rule.checkVariant == "backDatedEditing":
                                        min_allowed_date = (datetime.now()-timedelta(single_rule.ruleNumValue)).date()
                                        testResult = objDate.date() < min_allowed_date # True, if denied

                                    elif single_rule.checkVariant == "writePermission":
                                        testResult = bool(single_rule.ruleNumValue) # True, if denied
                                elif isinstance(args[0],dict):
                                    if args[0]["regExp"] and args[0]["testType"] == "match":
                                        testResult = bool(re.match(r'{}'.format(single_rule.ruleStrValue), args[0]["testValue"], re.I))
                                    elif args[0]["regExp"] and args[0]["testType"] == "search":
                                        testResult = bool(re.search(r'{}'.format(single_rule.ruleStrValue), args[0]["testValue"], re.I))

                                checksResult.append({"currentPriority":single_rule.rulePriority, "testResult":testResult, "testType":"ruleDeny"})

                            elif single_rule.ruleType == "ruleAllow":
                                testResult = False
                                if single_rule.checkVariant == "backDatedEditing":
                                    min_allowed_date = (datetime.now()-timedelta(single_rule.ruleNumValue)).date()
                                    testResult = objDate.date() >= min_allowed_date # True, if editing allowed

                                elif single_rule.checkVariant == "writePermission":
                                    testResult = bool(single_rule.ruleNumValue) # True, if allowed (when value is not zero)

                                checksResult.append({"currentPriority":single_rule.rulePriority, "testResult":testResult, "testType":"ruleAllow"})
        else:
            checksResult = [{"currentPriority":1, "testResult":True, "testType":"ruleDeny"}] # For testing purposes, deny access if user not found

        # Final checks analysis. Value of testResult meant, that rule matches criteria. 
        # It does not mean allow or deny, which depends on the testType

        if len(checksResult) == 1:
            if checksResult[0]['currentPriority'] == 0:
                # No rules were checked, action enabled by default
                return not checksResult[0]['testResult']

        cres = {"currentPriority":0, "testResult":False}
        for single_result in checksResult:
            if single_result.get("testType") != "ruleDeny":
                continue

            if single_result.get("currentPriority") == cres.get("currentPriority"):
                cres["testResult"] = cres.get("testResult") or single_result.get("testResult") # If any rule denies, then deny access to object

            elif single_result.get("currentPriority") > cres.get("currentPriority"):
                cres["testResult"] = single_result.get("testResult")
                cres["currentPriority"] = single_result.get("currentPriority")

        # Allow rules. Result of test is casting to deny rule (as it is a deny rule)
        for single_result in checksResult:
            if single_result.get("testType") != "ruleAllow":
                continue

            if single_result.get("currentPriority") == cres.get("currentPriority"):
                if not cres.get("testResult") and not single_result.get("testResult"):
                    cres["testResult"] = True
                else:
                    cres["testResult"] = cres.get("testResult") and not single_result.get("testResult")
            elif single_result.get("currentPriority") > cres.get("currentPriority"):
                cres["testResult"] = not single_result.get("testResult")
                cres["currentPriority"] = single_result.get("currentPriority")

        return not cres["testResult"]

    def extCallCheck(self, objectType, user_name, objDate_iso, stage, *args):
#        import pudb; pudb.set_trace()
        res=self._check_rule(objectType, user_name, objDate_iso, stage, *args)
        return res
