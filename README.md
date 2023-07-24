External user permissions control module for old 1C configurations

This addon processes JSON request to the Odoo server with the following data structure:
(request example can be seen at the end)

- Object type (actual dictionary values are selected by the developer)
- User name (in the external system)
- Date, associated with the object
- mode (for now it is only "write", the key is reserved for future modifications)
- additional parameters, in a dictionary

Additional parameters:
- regEx key, always True (reserved for future modifications)
- testType key, "match" or "search"
- testValue key

Rules are applied to user groups. Addon user groups do not inherit Odoo user groups, it is standalone model. Users can be included in more than one group at the same time.
Rules allow or deny access depending on the specified condition (as shown in diagram 1). Also rules have priority field, which is useful for some scenarios. Test result, priority and type of the rule are placed in the dictionary. These dictionaries, in turn, are placed in a list.
Then, analysing this list, a decision is made as to whether or not to allow access (according to diagram 2).

The return value False is considered to allow action and True is considered to deny it respectively.
Addon is experimental and in "proof-of-concept" state, so it is not recommended to use it on real databases without thorough testing.

Diagram 1
```mermaid
flowchart TD
    A([Current rule check]) --> B{Is this rule of deny type?}
    B -->|No| AllowRuleCheck{Is this rule of write allow type?}
    AllowRuleCheck --> |Yes|WriteEnabledCheckAllowRule["`If field ruleNumValue > 0, then set value to True (rule is fulfilled, operation is **allowed**)`"]
    AllowRuleCheck --> |No|CheckObjectDateAllowRule["`If data in parameter **is later than (or equal to)** date in the rule, then set value to True (rule is fulfilled, operation is **allowed**)`"]
    WriteEnabledCheckAllowRule --> MainCheckFinished
    CheckObjectDateAllowRule --> MainCheckFinished
    %% For the rules with Allow type check result of True means to Allow operation, For the rules with Deny type - operation denied, respectively
    B -->|Yes| C{Is there additional parameters?}
    C -->|No| SimpleChecks{Is this rule of Write allow type?}
    SimpleChecks -->|Yes| WriteEnabledCheckDenyRule["`If field ruleNumValue > 0, then set value to True (rule is fulfilled, operation is **denied**)`"]
    SimpleChecks -->|No| CheckObjectDateDenyRule["`If data in parameter **is earlier** than date in the rule, then set value to True (rule is fulfilled, operation is **denied**)`"]
    C -->|Yes| D{Check rule with RegEx match method?}
    D -->|Yes| G["`Checks testValue for exact equality with field ruleStrValue of the rule. Letter case is ignored.`"]
    D -->|No| E["`Checks testValue against the pattern with field ruleStrValue of the rule. Method RegEx search. Letter case is ignored.`"]
    G --> MainCheckFinished
    E --> MainCheckFinished(["`Put the result in the dictionary, add the dictionary to the results list. Move to the next rule.`"])
    WriteEnabledCheckDenyRule --> MainCheckFinished
    CheckObjectDateDenyRule --> MainCheckFinished
```
Diagram 2
```mermaid
flowchart TD
CStart(["Analize check results"])-->cursorInit["`cursor: priority = 0, value = False`"]
cursorInit -->|for-each cycle| A{{"currResult of checkResults"}}
A--> B{Is currResult of the Deny rule?}
B -->|No| A
B -->|Yes| cursorCheck{Is current rule priority equal to cursor?}
cursorCheck-->|Yes| cursorSet["`cursor: value = value **OR** currResult.value (if any of the rules with the same priority deny operation, than operation denied) `"]
cursorCheck-->|No| C{Is currResult priority higher than cursor?}
C-->|Yes| D[Set cursor value and priority to currResult values]
D--> A
C-->|No| A
cursorSet-->A
A-->|Cycle for deny rules is finished, go to </br>next cycle, for allow rules. </br> for-each cycle| E1{{"currResult of checkResults"}}
E1--> F{Is currResult of the Allow rule?}
F-->|No| E1
F-->|Yes| cursorCheck2{Is currResult priority equal to cursor?}
cursorCheck2-->|Yes| cursorCheck3{"`Is **NOT** cursor.value **AND NOT** currResult.value?`"}
cursorCheck3-->|Yes| cursorSet3["`cursor: value = True (that means, that Allow rule denies operation)`"]
cursorCheck3-->|No| cursorSet2["`cursor: value **AND NOT** currResult.value (denies action only if both rules - Deny and Allow are denying action)`"]
cursorCheck2-->|No| cursorCheck2_1{Is currResult priority > cursor}
cursorCheck2_1-->|Yes| cursorSet4[Set cursor value and priority to currResult values]
cursorCheck2_1-->|No| E1
cursorSet4--> E1
cursorSet3--> E1
cursorSet2--> E1
E1==>|End of Allow type cycle is the end of the algoritm| CEnd(["`Analize finished, **return cursor value.**`"])
```

JSON request format example:
{
"jsonrpc": "2.0",
"method": "call",
"params": {
"args": [
"odoo_database_name",
user_id (here should be specific value. admin, for example, is usually 2 by default),
"passwd",
"acs1crules.usr1crules",
"extCallCheck",
[],
"DocProductsSaleOrder",
"Dennis",
"2023-06-17",
"write",
{
"regExp": true,
"testType": "match",
"testValue": "CDB00161"
}
],
"method": "execute",
"service": "object"
},
"id": null
}
