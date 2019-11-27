def __pl_resolve(kb, ci, cj):
    clauses = []
    # print("ci = ", ci)
    # print("cj = ", cj)
    for di in enum_disjunctions(ci):
        for dj in enum_disjunctions(cj):
            unsigned_di = copy.deepcopy(di)
            unsigned_dj = copy.deepcopy(dj)
            di_neg = False
            dj_neg = False
            if di.operator == '~':
                unsigned_di = (convert_to_cnf(~di))
                di_neg = True
            if dj.operator == '~':
                unsigned_dj = (convert_to_cnf(~dj))
                dj_neg = True

            # print("original_di: " + str(di) + " original_dj: " + str(dj))
            if unsigned_di.__equalOp__(unsigned_dj) and (di_neg != dj_neg):
                phi = unify(di, convert_to_cnf(~dj))
                if phi is not None:
                    new_clause = join_terms('|', unique(remove_all(di, enum_disjunctions(ci))) +
                                            remove_all(dj, enum_disjunctions(cj)))
                    resolvent = subst(phi, new_clause)
                    # print(len(loop_detector))
                    if resolvent is not False:
                        resolvent = factorize(resolvent)
                    clauses.append(resolvent)
    return clauses

def __pl_resolution(kb, alpha):
    clauses = kb.clauses + enum_conjunctions(convert_to_cnf(~alpha))
    new = set()
    while True:
        n = len(clauses)
        start_time = timer()
        pairs = [(clauses[i], clauses[j])
                 for i in range(n) for j in range(i + 1, n)]
        for (ci, cj) in pairs:
            resolvers = kb.__pl_resolve(ci, cj)
            if False in resolvers:
                return True
            new = new.union(set(resolvers))
        if new.issubset(set(clauses)):
            return False
        for c in new:
            if c not in clauses:
                clauses.append(c)
        elapsed_time = timer()
        if (elapsed_time - start_time) > MAX_TIME_PER_QUERY_FULL_RESOLUTION:
            return False