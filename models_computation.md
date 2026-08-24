# Chatpter 2 - Models of computation
### What is a model?
A way to describe the system we want to build. Breakdown into tasks and we need a requirements list and a process list. Models are simplifications of a real system/programs/processes or another model. It only conserves the properties that are relevant for the task that you want to study. Mardwell calls it System Under Design. 
            
          real system --> simplified represenattion --> model
The real systems are too complex to represent them as a whole so they are divided in parts (hierarchy).
- Behavioral hierarchy: organizes the states, events, alarms...
- Structural hierarchy: organizes the phyiscal components (CPU, memory, sesnors...)
Concurrency: more than one component workign and the samen time. Different things happening simultaneosly. They need to be synchronized and to communicate between them to share information.
Timing:Mardwel mentions 4 important necesities: measure the elapsed time, delay processes, use timeouts before doing something and use deadlines.
