package org.basex.query.expr;

import org.basex.query.*;
import org.basex.query.iter.*;
import org.basex.query.value.*;
import org.basex.query.value.item.*;
import org.basex.query.value.seq.*;
import org.basex.query.var.*;
import org.basex.util.*;
import org.basex.util.hash.*;

/**
 * Simple map expression: iterative evaluation with two operands (the last one yielding items).
 *
 * @author BaseX Team 2005-20, BSD License
 * @author Christian Gruen
 */
public final class DualMap extends SimpleMap {
  /**
   * Constructor.
   * @param info input info
   * @param exprs expressions
   */
  DualMap(final InputInfo info, final Expr... exprs) {
    super(info, exprs);
  }

  @Override
  public Iter iter(final QueryContext qc) {
    return new Iter() {
      final QueryFocus focus = new QueryFocus();
      Iter iter;

      @Override
      public Item next() throws QueryException {
        final QueryFocus qf = qc.focus;
        if(iter == null) iter = exprs[0].iter(qc);
        qc.focus = focus;
        try {
          do {
            // evaluate left operand
            focus.value = qf.value;
            Item item = qc.next(iter);
            if(item == null) return null;
            // evaluate right operand (yielding an item)
            focus.value = item;
            item = exprs[1].item(qc, info);
            if(item != Empty.VALUE) return item;
          } while(true);
        } finally {
          qc.focus = qf;
        }
      }
    };
  }

  @Override
  public Value value(final QueryContext qc) throws QueryException {
    return iter(qc).value(qc, this);
  }

  @Override
  public DualMap copy(final CompileContext cc, final IntObjMap<Var> vm) {
    return copyType(new DualMap(info, Arr.copyAll(cc, vm, exprs)));
  }

  @Override
  public String description() {
    return "iterative dual " + super.description();
  }
}