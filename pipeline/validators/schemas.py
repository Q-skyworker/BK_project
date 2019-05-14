# -*- coding: utf-8 -*-

KEY_PATTERN = "^((\\$\\{[a-zA-Z0-9_]{0,19}\\})|([a-zA-Z0-9_]{0,19}))$"

WEB_PIPELINE_SCHEMA = {
    "definitions": {},
    "$schema": "http://json-schema.org/draft-06/schema#",
    "$id": "http://example.com/example.json",
    "type": "object",
    "properties": {
        "start_event": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string", "enum": ["EmptyStartEvent"]},
                "outgoing": {"type": "string"}
            },
            "required": [
                "id",
                "name",
                "type",
                "outgoing"
            ]
        },
        "end_event": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "type": {"type": "string", "enum": ["EmptyEndEvent"]},
                "incoming": {"type": "string"},
            },
            "required": [
                "id",
                "name",
                "type",
                "incoming",
            ]
        },
        "flows": {
            "type": "object",
            "patternProperties": {
                "^\\w+$": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "source": {"type": "string"},
                        "target": {"type": "string"}
                    },
                    "required": [
                        "id", "source", "target"
                    ]
                }
            }

        },
        "gateways": {
            "type": "object",
            "patternProperties": {
                "^\\w+$": {
                    "oneOf": [
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {"type": "string", "enum": ["ConvergeGateway"]},
                                "name": {"type": "string", "maxLength": 40},
                                "incoming": {
                                    "anyOf": [
                                        {"type": "string"},
                                        {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    ]
                                },
                                "outgoing": {
                                    "anyOf": [
                                        {"type": "string"},
                                        {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    ]
                                }
                            },
                            "required": [
                                "id", "type", "name", "incoming", "outgoing"
                            ]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {"type": "string", "enum": ["ParallelGateway"]},
                                "name": {"type": "string", "maxLength": 40},
                                "incoming": {
                                    "anyOf": [
                                        {"type": "string"},
                                        {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    ]
                                },
                                "outgoing": {
                                    "anyOf": [
                                        {"type": "string"},
                                        {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    ]
                                }
                            },
                            "required": [
                                "id", "type", "name", "incoming", "outgoing",
                            ]
                        },
                        {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "type": {"type": "string", "enum": ["ExclusiveGateway"]},
                                "name": {"type": "string", "maxLength": 40},
                                "conditions": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^\\w+$": {
                                            "type": "object",
                                            "properties": {
                                                "evaluate": {"type": "string"},
                                                "tag": {"type": "string"}
                                            },
                                            "required": [
                                                "evaluate", "tag"
                                            ]
                                        }
                                    }
                                },
                                "incoming": {
                                    "anyOf": [
                                        {"type": "string"},
                                        {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    ]
                                },
                                "outgoing": {
                                    "anyOf": [
                                        {"type": "string"},
                                        {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    ]
                                }
                            },
                            "required": [
                                "id", "type", "name", "incoming", "outgoing", "conditions"
                            ]
                        }
                    ]

                }
            }
        },
        "activities": {
            "type": "object",
            "patternProperties": {
                "^\\w+$": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "type": {"type": "string", "enum": ["ServiceActivity", "SubProcess"]},
                        "name": {"type": "string", "minLength": 1, "maxLength": 40},
                        # "error_ignorable": {"type": "boolean"},
                        "incoming": {"type": "string"},
                        "outgoing": {"type": "string"},
                        "component": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "string"},
                                "data": {
                                    "type": "object",
                                    "patternProperties": {
                                        "^\\w+$": {
                                            "type": "object",
                                            "properties": {
                                                "hook": {"type": "boolean"},
                                                "value": {
                                                    "type": ["string", "boolean", "object", "null", "number", "array"]}
                                            },
                                            "required": [
                                                "hook", "value"
                                            ]
                                        }
                                    }
                                }
                            },
                            "required": [
                                "code", "data"
                            ]
                        }
                    },
                    "required": [
                        "id", "name", "type", "incoming", "outgoing"
                    ]
                }
            }
        },
        "constants": {
            "type": "object",
            "patternProperties": {
                KEY_PATTERN: {
                    "type": "object",
                    "properties": {
                        "source_tag": {"type": "string"},
                        "name": {"type": "string", "minLength": 1, "maxLength": 20},
                        "custom_type": {"type": "string"},
                        "value": {"type": ["string", "number", "array", "boolean", "object", "null"]},
                        "source_type": {"type": "string", "enum": ["component_inputs", "component_outputs", "custom"]},
                        "validation": {"type": "string"},
                        "source_info": {
                            "type": "object",
                            "patternProperties": {
                                "^\\w+$": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                        },
                        "key": {
                            "type": "string",
                            "pattern": KEY_PATTERN
                        },
                        "desc": {"type": "string"},
                        "show_type": {"type": "string", "enum": ["show", "hide"]}
                    }
                }
            }
        },
        "outputs": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": KEY_PATTERN
            }
        }
    },
    "required": [
        "start_event",
        "end_event",
        "activities",
        "gateways",
        "outputs",
        "constants"
    ]
}
