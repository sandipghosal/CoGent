from common_imports import (
    Path, ET, Enum, auto,
    log, SOLVER, dataclass, field, deque,
    List, Any, Dict, Optional, Tuple, Union
)

from constraintbuilder import Expression
# from conditionbuilder import Contract


######################################
# Classes and Function for Data Types
######################################

class DataType(Enum):
    '''
    Class DataType creates enumerated constants.
    A variable can take only one value from the following constants
    '''
    INT = "int"
    FLOAT = "float"
    DOUBLE = "double"
    STRING = "string"
    BOOL = "bool"


def parse_datatype(s: str) -> DataType:
    '''
    Parse the datatype from the given XML file
    '''
    s = s.strip().lower()
    if s in ("int"):
        return DataType.INT
    elif s in ("float"):
        return DataType.FLOAT
    # elif s in ("double"):
    #     return DataType.DOUBLE
    elif s in ("bool"):
        return DataType.BOOL
    else:
        return DataType.STRING


def cast_value(text: str, type: DataType):
    '''
    Typecast the text read from XML file to appropriate type
    '''
    if text is None:
        return None
    t = text.strip()
    if type == DataType.INT:
        return int(t)
    elif type == DataType.FLOAT:
        return float(t)
    elif type == DataType.DOUBLE:
        return float(t)
    elif type == DataType.BOOL:
        if t.lower() in ("true", "t", "1"):
            return True
        if t.lower() in ("false", "f", "0"):
            return False
        raise ValueError(f"Cannot parse bool from '{text}'")
    else:
        return str(t)
    

###############################################
# Classes for Variables, Registers and Constant
###############################################


@dataclass
class Variable:
    '''
    Class Variable for method input parameters and free variables
    used in a contract
    '''
    name : str
    typ : DataType
    solver_exp: Any = field(init=False, default=None)
    # value which can be type of either int or float or bool or str
    # or none of them
    value : Optional[Union[int, float, bool, str]] = None

    def to_solver_expr(self):
        if self.solver_exp is None:
            if self.typ == DataType.INT:
                self.solver_exp = SOLVER.int(self.name)
        return self.solver_exp
    
    def set_value(self, val) -> None:
        if self.typ == DataType.INT:
            self.value = int(val)

    def __repr__(self):
         return str(self.value) if self.value is not None else self.name


@dataclass
class Register:
    '''
    Storage cell for each location (comes from <globals> in XML)
    '''
    name: str
    typ: DataType
    value: Optional[Union[int, float, bool, str]] = None
    solver_exp: Any = field(init=False, default=None)

    def to_solver_expr(self):
        if self.solver_exp is None:
            if self.typ == DataType.INT:
                self.solver_exp = SOLVER.int(self.name)
        return self.solver_exp
    
    def set_value(self, val) -> None:
        if self.typ == DataType.INT:
            self.value = int(val)

    def __repr__(self):
        return self.name
    

@dataclass
class Constant:
    '''
    Class Variable for method input parameters and free variables
    used in a contract
    '''
    name : str
    typ : DataType
    # value which can be type of either int or float or bool or str
    # or none of them
    value : Optional[Union[int, float, bool, str]] = None
    solver_exp: Any = field(init=False, default=None)

    def to_solver_expr(self):
        if self.solver_exp is None:
            if self.typ == DataType.INT:
                self.solver_exp = SOLVER.int(self.name)
        return self.solver_exp
    
    def set_value(self, val) -> None:
        if self.typ == DataType.INT:
            self.value = int(val)

    def __repr__(self):
        return self.name
    

@dataclass
class ConstantPool:
    '''
    Pool for holding all constants (comes from <constants> in XML)
    '''
    # field(default_factory=dict) creates fresh dict for each 
    # class instance
    consts: Dict[str, Constant] = field(default_factory=dict)

    def add(self, const: Constant):
        if const.name in self.consts:
            raise KeyError(f"Duplicate constant: {const.name}")
        self.consts[const.name] = const

    def __contains__(self, k: str) -> bool:
        return k in self.consts
    
    def __getitem__(self, k: str) -> Constant:
        return self.consts[k]
    
    def __repr__(self) -> str:
        return "ConstantPool{" + ", ".join(repr(c) for c in self.consts.values()) + "}"




###############################################
# Symbols (Inputs and Methods; Outputs)
###############################################

# frozen=True makes the object read-only after initialization
# Cannot modify any attribute after the object is created
# any attempt of modification will raise a FrozenInstanceError
@dataclass(frozen=False)
class Param(Variable):
    '''
    Class for each parameter to a method
    '''

    def __repr__(self):
        return self.name

    def to_solver_expr(self):
        if self.solver_exp is None:
            if self.typ == DataType.INT:
                self.solver_exp = SOLVER.int(self.name)
        return self.solver_exp

class OutputKind(Enum):
    '''
    Different kind of output a method can possibly returns
    '''
    # auto() assigns incrementing integers, starting from 1
    # No two member share the same number
    TRUE = auto()
    FALSE = auto()
    VOID = auto()   # given as 'V' in XML
    ERROR = auto()  # __ERR
    VALUE = auto()  # output with params, e.g., O_pop(p1)
    MUL = auto()    # output/returning multiple values 
    OTHER = auto()
        
@dataclass
class Symbol:
    '''
    These are the symbols given in XML file under <symbol> tag
    '''
    name: str
    params: List[Param] = field(default_factory=None)

    def signature(self) -> str:
        if not self.params:
            return f"{self.name}()"
        sig = ", ".join(f"{p.name}" for p in self.params)
        return f"{self.name}({sig})"
    
    def __repr__(self):
        return self.signature()
    
@dataclass
class Output(Symbol):
    kind: OutputKind = field(init=True, default_factory=OutputKind.OTHER)
    output: Any = field(default=None)

    def __repr__(self):
        if self.kind == OutputKind.TRUE:
            return 'True'
        elif self.kind == OutputKind.FALSE:
            return 'False'
        elif self.kind in [OutputKind.VALUE, OutputKind.MUL]:
            return f'{self.output}'
        elif self.kind == OutputKind.ERROR:
            return 'Error'
        elif self.kind == OutputKind.VOID:
            return 'Void'
        else:
            return 'Not Found'

@dataclass(repr=False) # disable auto __repr__ for Method
class Method(Symbol):
    '''
    Input methods e.g., push, pop, isempty, contains.
    These correspond to API methods/observers.
    '''
    # logical condition over registers and input parameters
    condition: Optional[Expression] = None
    
    # method's output type
    output_kind : Optional[OutputKind] = None

    # output parameters (for returning values)
    output_params: List[Param] = field(default_factory=list)

    # method's output can be True/False/Constant
    output: Any = field(init=True, default=None)



def parse_output(name: str, params: List[Param]) -> OutputKind:
    '''
    Process output read from XML file and prepare corresponding
    Output object
    '''
    u = name.upper()
    if u == 'TRUE':
        return OutputKind.TRUE
    elif u == 'FALSE':
        return OutputKind.FALSE
    elif u in ("V", "VOID"):
        return OutputKind.VOID
    elif u in ("__ERR", "ERR", "ERROR"):
        return OutputKind.ERROR
    if params:
        return OutputKind.VALUE
    else:
        return OutputKind.OTHER



###############################################
# Locations and Transitions
###############################################


@dataclass
class Location:
    name: str
    start_loc: bool = False
    registers: Optional[str] = field(default_factory=set)
    invariant: Optional[Expression] = None
    contracts: Optional[Any] = field(default_factory=list)

    def __repr__(self):
        return self.name

@dataclass
class Assignment:
    target_reg: Register
    expr:str

    def __repr__(self) -> str:
        return f"{self.target_reg}={self.expr}"
    
@dataclass
class Transition:
    source: Location
    dest: Location
    input: Optional[Method] = None    
    assignments: List[Assignment] = field(default_factory=list)   
    output: Optional[Output] = None
    #guard: Optional[str] = None
    # Bind some output such as O_pop with parameters
    # output_params_binding: List[str] = field(default_factory=list)

    def __post_init__(self):
        if (self.input is None) and (self.output is None):
            raise ValueError("Transition must have exactly one of 'input' or 'output' set")

    @property
    # @property is a decorator that lets you access a method like an attribute.
    # So instead of writing tr.is_input() we can write tr.is_input
    def is_input(self) -> bool:
        return self.input is not None
    
    @property
    def is_output(self) -> bool:
        return self.output is not None
    
    @property
    def is_io(self) -> bool:
        return self.input is not None and self.output is not None

    @property
    def symbol_name(self) -> str:
        # for indexing/lookup by symbol, prefer input name if present(IO or IN)
        # otherwise output name
        return self.input.name if self.input else (self.output.name
                                                   if self.Output else "<none>")
    
    def __repr__(self) -> str:
        if self.input is None:
            return f"{self.source}:{self.input}:{self.assignments}:{self.output}:{self.dest}"
        else:
            return f"{self.source}:{self.input}:{self.input.condition}:{self.assignments}:{self.output}:{self.dest}"



###############################################
# The Automaton
###############################################

@dataclass
class Automaton:
    # Alphabets
    inputs: Dict[str, Method] = field(default_factory=dict)
    outputs: Dict[str, Output] = field(default_factory=dict)
    observers: Dict[str, Method] = field(default_factory=dict)

    # Pools
    constants: ConstantPool = field(default_factory=ConstantPool)
    registers: Dict[str, Register] = field(default_factory=list)
    
    # Graph
    locations: Dict[str, Location] = field(default_factory=dict)
    transitions: List[Transition] = field(default_factory=list)

    # Indices
    trans_by_loc: Dict[str, List[Transition]] = field(default_factory=dict, init = False)
    trans_into_loc: Dict[str, List[Transition]] = field(default_factory=dict, init = False)
    trans_by_loc_sym: Dict[Tuple[str, str], List[Transition]] = field(default_factory=dict, init=False)
    trans_by_loc_out: Dict[Tuple[str, str], List[Transition]] = field(default_factory=dict, init=False)
    trans_by_loc_io: Dict[Tuple[str, str, str], List[Transition]] = field(default_factory=dict, init=False)
    trans_by_src_dst: Dict[Tuple[str, str], List[Transition]] = field(default_factory=dict, init=False)

    # Location specific predicates
    location_truth_predicates: Dict[str, List[Method]] = field(default_factory=dict, init=False)
    
    
    # ----------- Constructing the Automaton ----------------
    
    @staticmethod
    def from_file(path: Union[str, Path]) -> "Automaton":   # The quotes are a forward reference (used when the class may not yet be fully defined)
        log.debug('Extracting automaton from file ' + path)
        return Automaton.from_string(Path(path).read_text(encoding="utf-8"))
    
    @staticmethod
    def from_string(xml_file: str) -> "Automaton":
        root = ET.fromstring(xml_file)

        # (A) Get alphabets
        inputs: Dict[str, Method] = {}
        outputs: Dict[str, Output] = {}

        alphabet = root.find("alphabet")
        if alphabet is None:
            log.critical('Missing tag <alphabet>')
            raise ValueError("Missing tag <alphabet>")
        
        in_node = alphabet.find("inputs")
        if in_node is not None:
            for sym in in_node.findall("symbol"):
                name = sym.get("name")
                if not name:
                    log.critical('Missing <name> tag for symbol '+ sym)
                    raise ValueError("Missing <name> for <symbol> under <inputs>")
                params: List[Param] = []
                for p in sym.findall("param"):
                    pname = p.get("name")
                    ptyp = parse_datatype(p.get("type"))
                    params.append(Param(name=pname, typ=ptyp))
                inputs[name] = Method(name=name, params=params)
        log.debug(f"List of Input symbols: {', '.join(str(i) for i in inputs.values())}")

        out_node = alphabet.find("outputs")
        if out_node is not None:
            for sym in out_node.findall("symbol"):
                name = sym.get("name")
                if not name:
                    log.critical('Missing <name> tag for symbol '+ sym)
                    raise ValueError("Missing <name> for <symbol> under <outputs>")
                params: List[Param] = []
                for p in sym.findall("param"):
                    pname = p.get("name")
                    ptyp = parse_datatype(p.get("type"))
                    params.append(Param(name=pname, typ=ptyp))
                if len(params) > 1:
                    log.critical(f"Output symbol {name} has more than one parameters")
                    exit(1)
                kind = parse_output(name=name, params=params)
                outputs[name] = Output(name=name, params=params, kind=kind)
        log.debug(f"List of Output symbols: {', '.join(o for o in outputs)}")

        # (B) Get constants
        constants = ConstantPool()
        const_node = root.find("constants")
        if const_node is not None:
            for c in const_node.findall("constant"):
                cname = c.get("name")
                ctyp = parse_datatype(c.get("type"))
                cval = cast_value((c.text or "").strip(), ctyp)
                constants.add(Constant(name=cname, typ=ctyp, value=cval))
            log.debug(f"List of constants: {', '.join(c for c in constants.consts)}")


        # (C) Get registers
        registers: Dict[str, Register] = {}
        glob = root.find("globals")
        if glob is not None:
            for v in glob.findall("variable"):
                rname = v.get("name")
                rtyp = parse_datatype(v.get("type"))
                rval = cast_value((v.text or "").strip(), rtyp)
                registers[rname] = Register(name=rname, typ=rtyp, value=rval)
        log.debug(f"List of registers: {', '.join(r for r in registers)}")

        # (D) Get Locations
        locations: Dict[str, Location] = {}
        loc_node = root.find("locations")
        if loc_node is None:
            log.critical('<locations> tag is missing')
            raise ValueError("Missing <locations> in XML")
        init_seen = False
        for l in loc_node.findall("location"):
            lname = l.get("name")
            if not lname:
                log.critical('Missing <name> for location' + l)
                raise ValueError("Missing <name> for <location>")
            initial = (l.get("initial") == "true")
            locations[lname] = Location(name=lname, start_loc=initial)
            init_seen = init_seen or initial
        if not init_seen:
            log.critical('Start location not specified')
            raise ValueError("No start location specified")
        log.debug(f"List of locations: {", ".join(l for l in locations)}")
        
        # (E) Get Transitions
        transitions : List[Transition] = []
        trans_node = root.find("transitions")
        if trans_node is not None:
            for t in trans_node.findall("transition"):
                src_name = t.get("from")
                dest_name = t.get("to")
                sym_name = t.get("symbol")
                if src_name is None or dest_name is None or sym_name is None:
                    log.critical('Either <from> or <to> or <symbol> is missing for ' + str(t))
                    raise ValueError("<transition> must have <from>" \
                    "/<to>/<symbol> attributes")
                
                if src_name not in locations or dest_name not in locations:
                    log.critical('Either ' + src_name + ' or ' + dest_name+ ' is not specified earlier in XML file')
                    raise KeyError(f"Transition references to unknown location:{src_name}->{dest_name}")
                
                guard_expr: Optional[Expression] = None
                g = t.find("guard")
                if g is not None:
                    gtext = (g.text or "").strip()
                    if gtext:
                        guard_expr = Expression(gtext)
                else:
                    guard_expr = Expression('True')
                
                assigns: List[Assignment] = []
                a = t.find("assignments")
                if a is not None:
                    for asn in a.findall("assign"):
                        to = asn.get("to")
                        expr = (asn.text or "").strip()
                        if not to:
                            log.critical('<assign> tag is missing for transition from'+ src_name)
                            raise ValueError("<assign> mi   ssing 'to' attribute")
                        assigns.append(Assignment(target_reg=to, expr=expr))
                
                params_attr = t.get("params")
                out_params: List[str] = []
                if params_attr:
                    out_params = [p.strip() for p in params_attr.split(",") if p.strip()]

                resolved_input : Optional[Method] = None
                resolved_output: Optional[Output] = None
                if sym_name in inputs:
                    base_input = inputs[sym_name]
                    resolved_input = Method(
                        name=base_input.name,
                        params=list(base_input.params),
                        condition=guard_expr
                    )
                elif sym_name in outputs:
                    base_output = outputs[sym_name]
                    # assuming method has only one output
                    output = assigns[0].expr if assigns else None
                    resolved_output = Output(
                        name=base_output.name, 
                        params=list(out_params), 
                        kind=base_output.kind,
                        output=output
                    )
                else:
                    log.critical('Transition uses unknown symbol ' + sym_name)
                    raise KeyError("Transition uses unknown symbol '{sym_name}'")
                
                # create the Transition object`
                tr = Transition(
                    source=locations[src_name],
                    dest=locations[dest_name],
                    input=resolved_input,
                    output=resolved_output,
                    # guard=guard_text,
                    assignments=assigns,
                    # output_params_binding=out_params_binding
                )
                transitions.append(tr)
        # log.debug(
        #     "List of transitions:%s",
        #     ", ".join(str(t) for t in transitions)
        # )
        log.debug("List of transitions: ")
        for t in transitions:
            log.debug("     %s\n", t)
        log.debug("\n")

        A = Automaton(
            inputs=inputs,
            outputs=outputs,
            constants=constants,

            registers=registers,
            locations=locations,
            transitions=transitions
        )

        A._combine_in_out_transitions()
        
        # Merge IO transitions for observer outputs TRUE/FALSE at all locations
        from_types = {OutputKind.TRUE, OutputKind.FALSE}
        A._merge_same_io_transition_by_or(
            restrict_to_outputs=from_types,
            # Optionally restrict to observer methods only:
            # restrict_to_methods={"I_isfull", "I_isempty", "I_contains", "I_issize"}
        )
        A._compute_observers()
        A._infer_method_output_types()
        A._build_indices()
        A._populate_location_truth_predicates()
        A._compute_location_registers()
        A._compute_invariants()
        return A




    def _combine_in_out_transitions(self) -> None:
        '''
        Combines input-output transitions into single transition while
        keeping the output label on the combined edge.
        For any location m:
            - For each incoming pure input transition s -- I --> m
            - For each outgoing pur output transition m -- O --> t
            Create a single IO transition: s -- I/O --> t
            Guard: = (g_in) && (g_out) if both present
            Assignments := in. assignment + out.assignment
            output_params_binding := copied from the output transition
            The original input/output transition that were combined are removed.
        '''
        if not self.transitions:
            return
        
        outgoing_by_loc: Dict[str, List[Transition]] = {}
        incoming_by_loc: Dict[str, List[Transition]] = {}
        
        for tr in self.transitions:
            # Builds two dictionaries that group all transitions by their starting state and ending state.
            # If key exists -> return its value
            # If key does NOT exist:
            #   Insert it with default_value
            #   Return default_value
            # Example: If the transitions are as follows: A → B, A → C, B → C
            # outgoing_by_loc { "A": [A→B, A→C],"B": [B→C]} and 
            # incoming_by_loc {"B": [A→B], "C": [A→C, B→C]}

            outgoing_by_loc.setdefault(tr.source.name, []).append(tr)
            incoming_by_loc.setdefault(tr.dest.name, []).append(tr)

        def combine_guards(g1:Optional[Expression], g2:Optional[Expression]) -> Optional[Expression]:
            if g1 and g2:
                return Expression(g1.text + '&&' + g2.text)
            return Expression(g1.text + '||' + g2.text)
        
        new_transitions: List[Transition] = []
        consumed_ids: set[int] = set()
        # For each middle location m, connect every IN-> OUT into IO
        for m_name, outs in outgoing_by_loc.items():
            # OUT-only edges from m
            pure_outputs = [tr for tr in outs if tr.is_output]
            if not pure_outputs:
                continue
            # IN-only into m
            ins = [tr for tr in incoming_by_loc.get(m_name, []) if tr.is_input]
            if not ins:
                continue

            for in_tr in ins:
                for out_tr in pure_outputs:
                    # since out transition does not have guard, hence no need to combine guards of output transition
                    # commenting the function call combine_guards
                    # combine_guard = combine_guards(in_tr.input.condition, out_tr.input.condition)
                    combine_assigns = in_tr.assignments + out_tr.assignments
                    io_tr = Transition(
                        source=in_tr.source,
                        dest=out_tr.dest,
                        input=in_tr.input,
                        output=out_tr.output,
                        assignments=combine_assigns,
                        # output_params_binding=list(out_tr.output_params_binding)
                    )
                    new_transitions.append(io_tr)

                consumed_ids.add(id(in_tr))

            for out_tr in pure_outputs:
                consumed_ids.add(id(out_tr))

        # keep everything else same
        for tr in self.transitions:
            if id(tr) not in consumed_ids:
                new_transitions.append(tr)

        self.transitions = new_transitions
        # log.debug(
        #     "List of transitions after merging in and out transitions:\n%s",
        #     ", ".join(str(t) for t in self.transitions)
        # )
        log.debug("List of transitions after merging in and out transitions: ")
        for t in self.transitions:
            log.debug("     %s\n", t)
        log.debug("\n")

        def remove_middle_locations()-> None:
            '''
            Remove intermediate locations k since
            tranistion s->k and k->t has been joined into a
            single transition s->t
            '''
            locs = set()
            for tr in self.transitions:
                locs.add(tr.source.name)
                locs.add(tr.dest.name)
            self.locations = {
                name: loc for name, loc in self.locations.items()
                if name in locs
            }
            log.debug('List of locations after removing intermediate locations: %s\n',
                      ", ".join(self.locations.keys()))

        remove_middle_locations()    
    
    def _merge_same_io_transition_by_or(self, 
                                       *,
                                       restrict_to_outputs: Optional[set] = None,
                                       # e.g., {OutputKind.TRUE, OutputKind.FALSE}
                                       restrict_to_methods: Optional[set] = None,
                                       # e.g., {"I_isfull", "I_isempty", "I_contains", "I_issize"}
                                       ) -> None:
        '''
        Merge IO transitions (input + output) that:
        - have same src, dest, method, assignments, bindings
        - differ only in guards
        Policy:
            TRUE -> OR guards
            FALSE -> AND guards
        '''

        if not self.transitions:
            return
        
        buckets: Dict[
            Tuple[
                str,    # src
                str,    # dest
                str,    # method
                Tuple[Tuple[str, str], ...],    # assignments
                Output                # output
            ],
            List[Transition]
        ] = {}

        # Helper to canonicalized assignments (order-insensitive, register identity agnostic)
        def _assignments_key(assigns: List[Assignment]) -> Tuple[Tuple[str, str], ...]:
            return tuple(sorted((a.target_reg.name, a.expr) for a in assigns))
        
        def _merge_guards(guards: List[Expression], *, op: str) -> Expression:
            '''
            op in {"OR", "AND"}
            '''
            uniq = []
            seen = set()
            for g in guards:
                txt = g.text.strip()
                if txt and txt not in seen:
                        uniq.append(txt)
                        seen.add(txt)
            
            if not uniq:
                return Expression("True")
            
            if len(uniq) == 1:
                return Expression(uniq[0])
            
            joiner = " || " if op == "OR" else " && "
            merged = joiner.join(f"({t})" for t in uniq)
            return Expression(merged)

        for tr in self.transitions:
            if not tr.is_io:
                continue
            if restrict_to_methods and tr.input.name not in restrict_to_methods:
                continue
            if restrict_to_outputs and tr.output.kind not in restrict_to_outputs:
                continue
            
            key = (
                tr.source.name,
                tr.dest.name,
                tr.input.name,
                tr.output.kind,
                _assignments_key(tr.assignments),
                # tuple(tr.output_params_binding)
            )
            buckets.setdefault(key, []).append(tr)

        if not buckets:
            return
        
        new_transitions: List[Transition] = []
        consumed: set[int] = set()

        for key, trs in buckets.items():
            if len(trs) == 1:
                continue

            _, _, _, out_kind, *_ = key
            op = "OR" if out_kind == OutputKind.TRUE else "AND"

            guards = [tr.input.condition for tr in trs]
            merged_guard = _merge_guards(guards, op=op)
            t0 = trs[0]

            merged_input = Method(
                name=t0.input.name,
                params=t0.input.params,
                condition=merged_guard,
                output_kind=t0.input.output_kind,
                output=t0.input.output,
                output_params=t0.input.output_params
            )

            merged = Transition(
                source=t0.source,
                dest=t0.dest,
                input=merged_input,
                output=t0.output,
                assignments=list(t0.assignments),
                # output_params_binding=list(t0.output_params_binding)
            )

            new_transitions.append(merged)

            for tr in trs:
                consumed.add(id(tr))

        for tr in self.transitions:
            if id(tr) not in consumed:
                new_transitions.append(tr)

        self.transitions = new_transitions

        # log.debug(
        #     "Transitions after merging IO TRUE/AND | FALSE/OR guards:\n%s\n",
        #     ", ".join(str(t) for t in self.transitions)
        # )
        log.debug("Transitions after merging IO TRUE/AND | FALSE/OR guards: ")
        for t in self.transitions:
            log.debug("     %s\n", t)
        log.debug("\n")
    

    def _compute_observers(self)->None:
        '''
        Populate self.observers as a subset of inputs such that
        - all transitions for those inputs are self-loops
        '''
        method_to_trans: Dict[str, List[Transition]] = {}

        for tr in self.transitions:
            if tr.input is None:
                continue
            method_to_trans.setdefault(tr.input.name, []).append(tr)

        observers: Dict[str, Method] = {}
        for m_name, trs in method_to_trans.items():
            is_observer = all(
                # tr.source.name == tr.dest.name and not tr.assignments
                tr.source.name == tr.dest.name
                for tr in trs
            )

            if is_observer:
                observers[m_name] = self.inputs[m_name]

        self.observers = observers
        log.debug(f'List of observers identified: {", ".join(o for o in self.observers)}\n')


    def _build_indices(self) -> None:
        '''
        Build the indices for easy lookup
        - trans_by_loc[loc]                   -> List[Transition]  (all outgoing)
        - trans_into_loc[loc]                 -> List[Transition]  (all incoming)
        - trans_by_loc_sym[(loc, input)]      -> List[Transition]  (IN + IO carrying that input)
        - trans_by_loc_out[(loc, output)]       -> List[Transition]  (OUT + IO carrying that output)
        - trans_by_loc_io[(loc, input, output)]  -> List[Transition]  (IO only)
        - trans_by_src_dst[(src, dst)]        -> List[Transition]  (all edges between src and dst)
        '''

        # clear all indices
        self.trans_by_loc.clear()
        self.trans_into_loc.clear()
        self.trans_by_loc_sym.clear()
        self.trans_by_loc_out.clear()
        self.trans_by_loc_io.clear()
        self.trans_by_src_dst.clear()

        for tr in self.transitions:
            src = tr.source.name
            dest = tr.dest.name

            # outgoing/incoming
            self.trans_by_loc.setdefault(src, []).append(tr)
            self.trans_into_loc.setdefault(dest, []).append(tr)

            # source-destination pair
            self.trans_by_src_dst.setdefault((src, dest), []).append(tr)

            # input-based index: include IN and IO transitions
            if tr.input is not None:
                self.trans_by_loc_sym.setdefault((src, tr.input.name), []).append(tr)

            # output-based index: include OUT and IO transitions
            if tr.output is not None:
                self.trans_by_loc_out.setdefault((src, tr.output.name), []).append(tr)

            # IO pair index: only when both present
            if tr.input is not None and tr.output.name is not None:
                self.trans_by_loc_io.setdefault((src, tr.input.name, tr.output.name), []).append(tr)

    # Find the outgoing transitions from a location
    def outgoing(self, loc_name: str) -> List[Transition]:
        return self.trans_by_loc.get(loc_name, [])
    
    # Find incoming transitions to a location
    def incoming(self, loc_name: str) -> List[Transition]:
        return self.trans_into_loc.get(loc_name, [])
    
    # Find outgoing transitions in a location for a input symbol
    def outgoing_for_input(self, loc_name: str, input_name: str) -> List[Transition]:
        return self.trans_by_loc_sym.get((loc_name, input_name), [])

    # Find outgoing transitions in a location giving specific output
    def outgoing_for_output(self, loc_name: str, output_name: str) -> List[Transition]:
        return self.trans_by_loc_out.get((loc_name, output_name), [])

    # Find transitions in a location for specific input and output
    def outgoing_for_io(self, loc_name: str, input_name: str, output_name: str) -> List[Transition]:
        return self.trans_by_loc_io.get((loc_name, input_name, output_name), [])

    # Find transitions between two given locations
    def between(self, src: str, dst: str) -> List[Transition]:
        return self.trans_by_src_dst.get((src, dst), [])


    def _populate_location_truth_predicates(self) -> None:
        '''
        Populate location-specific unparameterized observers whose guards are True
        on self-loop transitions.
        '''
        state_obs: Dict[str, List[Method]] = {}
        for loc in self.locations:
            valid_methods = []
            trs = self.trans_by_src_dst[(loc, loc)]
            if not trs:
                continue

            for tr in trs:
                if str(tr.input.condition).strip() == "True" \
                    and len(tr.input.params) == 0:
                    valid_methods.append(tr.input)

            state_obs[loc] = valid_methods

        self.location_truth_predicates = state_obs

    def _compute_location_registers(self) -> None:
        '''
        Compute for each location the set of registers available there
        '''
        for l in self.locations.values():
            for tr in self.incoming(l.name):
                for asn in tr.assignments:
                    l.registers.add(asn.target_reg)

    def _infer_method_output_types(self):
        """
        Infer output_kind and output_params for each method
        based on IO transitions
        """

        for tr in self.transitions:

            if not tr.is_io:
                continue

            method = tr.input
            out = tr.output

            if method is None or out is None:
                continue

            method.output_kind = out.kind

            if out.params:
                method.output_params = out.params
                # the rhs of assignments in out transition are the output
                for asn in tr.assignments:
                    if asn.expr in self.constants:
                        method.output = self.constants[asn.expr]
                    elif asn.expr in self.registers.keys():
                        method.output = self.registers[asn.expr]
                    else:
                        ValueError(f"In {tr} method outputs unknown value {asn.expr}")
            
            if method.output_kind is OutputKind.TRUE:
                method.output = True

            if method.output_kind is OutputKind.FALSE:
                method.output = False

            log.debug(f"In {tr} method {method} outputs {method.output}")
            
            if method.name in self.observers.keys():
                self.observers[method.name].output = out.output
                self.observers[method.name].output_kind = out.kind
                self.observers[method.name].output_params = out.params


    def _compute_invariants(self) -> None:
        for loc in self.locations.values():
            loc.invariant = Expression("False")
        
        start = next(l for l in self.locations.values() if l.start_loc)
        start.invariant = Expression("True")

        def join(e1: Expression, e2:Expression) -> Expression:
            if str(e1) == "False":
                return e2
            elif str(e2) == "False":
                return e1
            elif str(e1) == str(e2):
                return e1
            else:
                return Expression(f'({e1}) || ({e2})')

        worklist = deque([start])

        while worklist:
            curr = worklist.popleft()

            for tr in self.outgoing(curr.name):
                log.debug('\n')
                log.debug(f'Consider transition: {tr}')
                src_inv = curr.invariant
                log.debug(f'Derive postcondition for {tr.dest}:')
                new_inv = derive_sp(src_inv, tr, self)
                dst = tr.dest
                # merge with existing invariant at destination
                joined_inv = join(dst.invariant, new_inv)
                # check if changed
                if not (joined_inv == dst.invariant):
                    dst.invariant = joined_inv
                    log.debug(f'Invariant updated for {dst} to {joined_inv}\n')
                    worklist.append(dst)
                else:
                    log.debug(f'Invariant is unchanged for {dst}\n')
        
                    
###############################################
# Functions to derive postcondition
###############################################

def build_var_maps(A:Automaton, tr: Transition):
    reg_map ={}
    old_reg_map = {}
    param_map ={}

    for r in tr.dest.registers:
        reg_map[r] = A.registers[r].to_solver_expr()
        old_reg_map[r] = SOLVER.int(f'{r}_old')
        
        if tr.input:
            for p in tr.input.params:
                param_map[p.name] = p.to_solver_expr()

    return reg_map, old_reg_map, param_map

def substitute_old(expr, reg_map, old_reg_map):
    pairs = []
    quantified_vars = set()
    for name in reg_map:
        pairs.append((reg_map[name], old_reg_map[name]))
        quantified_vars.add(old_reg_map[name])
    return quantified_vars, SOLVER.substitute(expr, pairs)


def build_assignment_constraint(tr, reg_map, old_reg_map, param_map):
    '''
    Returns:
        (quantified_vars, constraint)
    
    quantified_vars: list of Z3 variables (old registers + params)
    constraint: Z3 formula
    '''
    constraints = SOLVER.bool_val(True)
    quantified_vars = set()

    if tr.dest.registers is not None:
        if tr.assignments is []:
            for r in tr.dest.registers:
                c = SOLVER._eq(reg_map[r], old_reg_map[r])
                quantified_vars.add(old_reg_map[r])
                constraints = SOLVER._and(constraints, c)
        else:
            for asn in tr.assignments:
                lhs = asn.target_reg
                rhs = asn.expr
                if rhs in param_map.keys():
                    c = SOLVER._eq(reg_map[lhs], param_map[rhs])
                    quantified_vars.add(param_map[rhs])
                    constraints = SOLVER._and(constraints, c)
                elif rhs in reg_map.keys():
                    c = SOLVER._eq(reg_map[lhs], old_reg_map[rhs])
                    quantified_vars.add(old_reg_map[rhs])
                    constraints = SOLVER._and(constraints, c)
                else:
                    ValueError("RHS of assignment should be a register or parameter")
    return quantified_vars, constraints


def derive_sp(pre: Expression, tr: Transition, A: Automaton) -> Expression:
    log.debug(f'Precondition: {pre}')
    log.debug(f'Guard: {tr.input.condition}')
    log.debug(f'Assignment: {tr.assignments}')
    reg_map, old_reg_map, param_map = build_var_maps(A, tr)
    set1, a_expr = build_assignment_constraint(tr, reg_map, old_reg_map, param_map)
    set2, p_expr = substitute_old(pre.to_solver_expr(), reg_map, old_reg_map)
    set3, g_expr = substitute_old(tr.input.condition.to_solver_expr(), reg_map, old_reg_map)
    quantified_vars = list(set1.union(set2, set3))
    expr = SOLVER.bool_val(True)
    for e in [a_expr, p_expr, g_expr]:
        expr = SOLVER._and(expr, e)

    if str(expr) not in ['True', 'False']:
        sp = SOLVER.eliminate(quantified_vars, expr)
    else:
        sp = expr
    e = Expression(str(sp))
    e.solver_expr = sp
    log.debug(f'Postcondition after quantifier elimination: {e}') 
    return e  