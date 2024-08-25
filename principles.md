Please describe your personal vision of the principles for organizing an effective team of collaborating people and AI agents that interact with each other.

* Every important task should be covered by metrics. These metrics can be based on the 
  work of LLMs themselves (both for dataset collection and evaluation), which helps 
  reduce labor intensity.
* It's necessary to analyze where an agent might fail in a way that could cause harm, 
  and cover these areas with additional checks or human audits. This is especially 
  important for autonomous agents that can initiate actions in the external environment, 
  such as changing code in a repository or spending money. The military sphere is 
  particularly dangerous, and during wartime, people tend to take more risks.
* Humans should be involved in the agents' work, but as the quality of work improves, 
  human intervention should decrease.
* For some important tasks, agents should not work directly but develop an intermediate 
  layer. For example, if we have a task for efficient elevator management, it's unclear 
  how to ensure it will always be controlled correctly if managed by an LLM (especially 
  with non-zero generation temperature). However, if our agent writes code to control 
  the elevator, we can test it and be confident in its deterministic behavior. Another 
  example: a model can analyze literature and create a set of rules for simpler models 
  to make decisions. Alternatively, important decisions should be made by several 
  different models - this is similar to how humans make important decisions.
* I'm convinced that we need to develop methods for extracting expert knowledge so 
  that agents can use the knowledge that often exists in an unformalized state in 
  people's minds. There are many techniques for this - this field was founded during 
  the early days of expert systems. I would be happy to try implementing some of these 
  ideas with AI agents.
* It's important not to exclude people but to try to leave them with less monotonous 
  and more creative tasks, increasing their productivity. This way, we won't receive 
  negative reactions or hidden resistance from people, but instead allow them to be 
  more confident about their future.