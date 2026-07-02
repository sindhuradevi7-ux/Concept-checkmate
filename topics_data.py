"""
topics_data.py
----------------
Seed data for ConceptCheckmate.

Each topic contains:
  - ideal_answer   : a model explanation (used for overall semantic similarity)
  - key_concepts   : atomic concept units the student SHOULD mention.
                      each has an id, a short label, the sentence/definition,
                      and a list of keyword synonyms used for lexical backup matching.
  - misconceptions : common wrong statements mapped to a corrective note.
                      detected via keyword pattern matching in the student transcript.

This file is intentionally editable — add your own topics before the interview
to match the interviewer's domain (SDE / Data / ML / Systems etc.)
"""

TOPICS = {
    "oop": {
        "title": "Object-Oriented Programming (OOP)",
        "ideal_answer": (
            "Object-Oriented Programming is a paradigm based on the concept of objects, "
            "which bundle data and behavior together. It rests on four pillars: encapsulation, "
            "which hides internal state and exposes behavior through methods; abstraction, which "
            "hides implementation complexity behind a simple interface; inheritance, which lets a "
            "class acquire properties and methods of a parent class to promote reuse; and "
            "polymorphism, which allows objects of different classes to be treated through a "
            "common interface, so the same method call can behave differently depending on the "
            "object's actual type."
        ),
        "key_concepts": [
            {"id": "encapsulation", "label": "Encapsulation", "keywords": ["encapsulation", "encapsulate", "hide data", "private", "getter", "setter"]},
            {"id": "abstraction", "label": "Abstraction", "keywords": ["abstraction", "abstract", "hide complexity", "interface", "simplify"]},
            {"id": "inheritance", "label": "Inheritance", "keywords": ["inheritance", "inherit", "parent class", "child class", "base class", "derived class", "reuse code"]},
            {"id": "polymorphism", "label": "Polymorphism", "keywords": ["polymorphism", "polymorphic", "overriding", "overloading", "many forms", "same interface"]},
            {"id": "class_object", "label": "Class vs Object", "keywords": ["class", "object", "instance", "blueprint"]},
        ],
        "misconceptions": [
            {"pattern": ["class", "object", "same thing"], "note": "A class is a blueprint; an object is a specific instance created from that blueprint. They are not the same thing."},
            {"pattern": ["polymorphism", "means", "many class"], "note": "Polymorphism means one interface can take many forms of behavior — it's not about having many classes."},
        ],
    },
    "osi_model": {
        "title": "OSI Model (Computer Networks)",
        "ideal_answer": (
            "The OSI model is a seven-layer conceptual framework used to standardize network "
            "communication. The Physical layer transmits raw bits over a medium. The Data Link "
            "layer handles node-to-node delivery and error detection using MAC addresses. The "
            "Network layer handles logical addressing and routing using IP addresses. The "
            "Transport layer ensures reliable end-to-end delivery, for example TCP, or fast "
            "unreliable delivery, for example UDP. The Session layer manages sessions between "
            "applications. The Presentation layer handles translation, encryption and compression "
            "of data. The Application layer is closest to the end user and provides network "
            "services directly to applications like HTTP or FTP."
        ),
        "key_concepts": [
            {"id": "physical", "label": "Physical Layer", "keywords": ["physical layer", "bits", "cable", "signal"]},
            {"id": "datalink", "label": "Data Link Layer", "keywords": ["data link", "mac address", "frame", "error detection"]},
            {"id": "network", "label": "Network Layer", "keywords": ["network layer", "ip address", "routing", "router"]},
            {"id": "transport", "label": "Transport Layer", "keywords": ["transport layer", "tcp", "udp", "reliable delivery", "port"]},
            {"id": "session", "label": "Session Layer", "keywords": ["session layer", "session management"]},
            {"id": "presentation", "label": "Presentation Layer", "keywords": ["presentation layer", "encryption", "compression", "translation"]},
            {"id": "application", "label": "Application Layer", "keywords": ["application layer", "http", "ftp", "end user"]},
        ],
        "misconceptions": [
            {"pattern": ["tcp", "layer", "3"], "note": "TCP operates at the Transport layer (Layer 4), not the Network layer (Layer 3)."},
            {"pattern": ["ip address", "mac address", "same"], "note": "IP addresses are logical (Network layer) while MAC addresses are physical/hardware (Data Link layer) — they serve different purposes."},
        ],
    },
    "dbms_normalization": {
        "title": "Database Normalization",
        "ideal_answer": (
            "Normalization is the process of organizing relational database tables to reduce data "
            "redundancy and avoid update, insertion and deletion anomalies. First Normal Form "
            "requires atomic column values with no repeating groups. Second Normal Form requires "
            "First Normal Form plus removal of partial dependency, meaning every non-key attribute "
            "must depend on the whole primary key. Third Normal Form requires Second Normal Form "
            "plus removal of transitive dependency, meaning non-key attributes must depend only on "
            "the primary key and not on other non-key attributes. Higher forms like BCNF handle "
            "edge cases involving multiple candidate keys."
        ),
        "key_concepts": [
            {"id": "goal", "label": "Goal: Reduce Redundancy", "keywords": ["redundancy", "anomaly", "duplicate data", "consistency"]},
            {"id": "1nf", "label": "1NF - Atomic Values", "keywords": ["first normal form", "1nf", "atomic value", "repeating group"]},
            {"id": "2nf", "label": "2NF - Partial Dependency", "keywords": ["second normal form", "2nf", "partial dependency", "composite key"]},
            {"id": "3nf", "label": "3NF - Transitive Dependency", "keywords": ["third normal form", "3nf", "transitive dependency"]},
            {"id": "primary_key", "label": "Primary / Candidate Key", "keywords": ["primary key", "candidate key", "foreign key"]},
        ],
        "misconceptions": [
            {"pattern": ["normalization", "increase", "redundancy"], "note": "Normalization reduces redundancy, it does not increase it — that's the opposite of its purpose."},
        ],
    },
    "photosynthesis": {
        "title": "Photosynthesis",
        "ideal_answer": (
            "Photosynthesis is the process by which green plants convert light energy into "
            "chemical energy stored in glucose. It occurs in the chloroplasts, where chlorophyll "
            "absorbs sunlight. The light-dependent reactions happen in the thylakoid membrane and "
            "split water molecules to release oxygen while producing ATP and NADPH. The light-"
            "independent reactions, known as the Calvin cycle, occur in the stroma and use ATP and "
            "NADPH to fix carbon dioxide into glucose. The overall inputs are carbon dioxide, water "
            "and light energy, and the outputs are glucose and oxygen."
        ),
        "key_concepts": [
            {"id": "location", "label": "Location: Chloroplast", "keywords": ["chloroplast", "chlorophyll", "thylakoid", "stroma"]},
            {"id": "light_reaction", "label": "Light-Dependent Reactions", "keywords": ["light reaction", "light dependent", "splits water", "oxygen released", "atp", "nadph"]},
            {"id": "calvin_cycle", "label": "Calvin Cycle", "keywords": ["calvin cycle", "light independent", "carbon fixation", "dark reaction"]},
            {"id": "inputs_outputs", "label": "Inputs & Outputs", "keywords": ["carbon dioxide", "water", "glucose", "oxygen", "sunlight"]},
        ],
        "misconceptions": [
            {"pattern": ["photosynthesis", "mitochondria"], "note": "Photosynthesis occurs in the chloroplast, not the mitochondria — mitochondria are the site of cellular respiration."},
            {"pattern": ["plants", "only", "night"], "note": "Photosynthesis requires light and happens during the day; respiration happens continuously."},
        ],
    },
    "machine_learning_basics": {
        "title": "Machine Learning Fundamentals",
        "ideal_answer": (
            "Machine learning is a field where systems learn patterns from data instead of being "
            "explicitly programmed with rules. In supervised learning, the model learns from "
            "labeled data to predict an output, covering tasks like classification and regression. "
            "In unsupervised learning, the model finds structure in unlabeled data, such as "
            "clustering or dimensionality reduction. Overfitting occurs when a model learns noise "
            "in the training data and performs poorly on unseen data, while underfitting occurs "
            "when a model is too simple to capture the underlying pattern. Techniques like cross "
            "validation, regularization and having a held-out test set help evaluate and improve "
            "generalization."
        ),
        "key_concepts": [
            {"id": "supervised", "label": "Supervised Learning", "keywords": ["supervised learning", "labeled data", "classification", "regression"]},
            {"id": "unsupervised", "label": "Unsupervised Learning", "keywords": ["unsupervised learning", "unlabeled data", "clustering", "dimensionality reduction"]},
            {"id": "overfitting", "label": "Overfitting", "keywords": ["overfitting", "overfit", "high variance", "noise", "memorize training"]},
            {"id": "underfitting", "label": "Underfitting", "keywords": ["underfitting", "underfit", "high bias", "too simple"]},
            {"id": "generalization", "label": "Generalization & Validation", "keywords": ["generalization", "cross validation", "regularization", "test set", "train test split"]},
        ],
        "misconceptions": [
            {"pattern": ["overfitting", "not enough data", "model too simple"], "note": "Overfitting is usually caused by excess model complexity relative to data, not by the model being too simple — that describes underfitting."},
        ],
    },
}


def list_topics():
    """Return a lightweight list for populating the UI dropdown."""
    return [{"id": key, "title": val["title"]} for key, val in TOPICS.items()]


def get_topic(topic_id):
    return TOPICS.get(topic_id)
