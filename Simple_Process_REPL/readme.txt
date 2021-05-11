# %s - An SPR Extension that does X.

This is a skeleton project for an SPR extension module.
is a simple python project that can be deployed to pip.
consists of a python file, a yaml file, and an spr file.

The Python code, core.py, imports whatever python libraries desired,
defines any extra functionality and wraps functions as needed.
has full as access to the SPR Application state which can contain
configuration section and an App state section for this module's use.

If this extension has one, the configuration will be located in 'config'
in the Application state. This state will be in the root of the application
state, all of this defined in core.yaml.
So define your data in core.yaml. Something like this.

```
    mymodule:
        foo: 10

    config:
        mymodule:
            bar: "this is bar, I need to have it."
```

really could be anywhere, named anything. Not smart.

SPR code is in core.spr. This where any extra symbols or partials related
this module's functionality can be defined.

To use this module within SPR make sure it is on your Python Path.
, in your SPR code create a namespace like so.

    namespace foo "some foo docstring" %s.core func1 func2 func3
