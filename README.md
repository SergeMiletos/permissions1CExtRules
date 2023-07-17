External user permissions control module for old 1C configurations

This addon processes JSON request with the following data structure:

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
Then, analysing this list, a decision is made as to whether or not to allow access(according to diagram 2).

```mermaid
flowchart TD
    A[Начало проверки текущего условия] --> B{Это <br/>запрещающее правило?}
    B -->|Да| C{Дополнительные параметры<br/> вызова существуют?}
    C -->|Да| D{Проверять условие <br/>методом RegEx match?}
    D -->|Да| G[Точное сравнение шаблона в правиле <br/>с входящим параметром testValue без учёта регистра]
    D -->|Нет| E[Сравнение шаблона в правиле с входящим параметром testValue <br/>методом search, соответственно в правиле шаблон /поле ruleStrValue/ <br/>должен быть задан с учётом возможностей этого метода.]
```
