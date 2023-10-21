# product_management_gbph
A GUI project manage program in python. 

# Main purpose
## Track your Todo(es)
1. Create and track your Todo(es), which can be postponed for several days you wish for infinite times until you 'finish' it.
2. A Todo may (or may not) have a father Project, and every Project can generate many Todo(es). The state of a Project can affect the state of its children Todo(es).
3. Add logs to the todo which you have done something about and postpone it to the date you need to take care of it again.
4. Todo(es) are arranged in a panel according to their different properties.
## Manage the Projects
1. A Project is considered a logical object that a Todo is affiliated to. In this software we focus on tracking our Todo(es), so a project is better considered an organiser of a series of Todo(es) and some other logs. Nevertheless, we still understand that projects are the ultimate aims.
2. In the case of sales project management(which is also the initial purpose of this GUI software), a project can be considered a product. 
3. A Project has many properties (or states) that can affect is weight, which indicates its importance.
4. to come: A Project can be assigned some programmatic Todo(es) on creation.
## Manage the Companies
1. A Company is considered a physical object that a Project is connected with. The children Todo(es) of a Project are all connected to the same company. An independent Todo can also be connected to a company.
2. A Company can be a client, a supplier, or any other physical organization. The idea is that a Todo usually has some connection with an external organization.
3. A Company has many properties and logs.

# How to launch
1. `pip install -r requirements.txt`
2. `python GBT_Pro.py`

# Release
Coming soon