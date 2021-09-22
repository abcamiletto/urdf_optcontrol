from matplotlib import pyplot as plt
from math import isinf
import numpy as np
from matplotlib.gridspec import GridSpec

def show(q, qd, qdd, q_limits, u, T, ee_pos, steps, cost_func, final_term, constr, f_constr):
    # Defining the X axis for most cases
    tgrid = [T / steps * k for k in range(steps + 1)]
    # Plotting Q and its derivatives
    fig1 = plot_q(q, qd, qdd, q_limits, u, tgrid)
    fig2 = plot_cost(q, qd, qdd, ee_pos, u, cost_func,final_term, tgrid)
    fig3 = plot_constraints(q, qd, qdd, ee_pos, u, constr, tgrid)
    return [fig1, fig2, *fig3]

def plot_q(q, qd, qdd, q_limits, u, tgrid):
    n_joints = len(q)
    # Setting for the plot axis
    gridspec_kw={   'width_ratios': [2, 1, 1, 1],
                    'wspace': 0.4,
                    'hspace': 0.4}

    fig, axes = plt.subplots(nrows=n_joints, ncols=4, figsize=(11,2.5*n_joints), gridspec_kw=gridspec_kw)

    for idx, ax in enumerate(axes):
        # Painting the boundaries
        lb, ub = q_limits['q'][0][idx], q_limits['q'][1][idx]
        if not isinf(lb) and not isinf(ub):
            ax[0].set_facecolor((1.0, 0.45, 0.4))
            ax[0].axhspan(lb, ub, facecolor='w')

        # Plotting the values
        ax[0].plot(tgrid, q[idx], '-')
        ax[0].legend('q_'+str(idx))
        ax[0].set_xlabel('time')
        ax[0].set_ylabel('q'+str(idx))

        # Painting the boundaries
        lb, ub = q_limits['qd'][0][idx], q_limits['qd'][1][idx]
        if not isinf(lb) and not isinf(ub):
            ax[1].set_facecolor((1.0, 0.45, 0.4))
            ax[1].axhspan(lb, ub, facecolor='w')

        ax[1].plot(tgrid, qd[idx], 'g-')
        ax[1].legend('qd_'+str(idx))
        ax[1].set_xlabel('time')

        ax[2].plot(tgrid[:-1], qdd[idx], 'y-')
        ax[2].legend('qdd_'+str(idx))
        ax[2].set_xlabel('time')

        lb, ub = q_limits['u'][0][idx], q_limits['u'][1][idx]
        if not isinf(lb) and not isinf(ub):
            ax[3].set_facecolor((1.0, 0.45, 0.4))
            ax[3].axhspan(lb, ub, facecolor='w')

        ax[3].plot(tgrid[:-1], u[idx], 'g-')
        ax[3].legend('ud_'+str(idx))
        ax[3].set_xlabel('time')

    return fig

def plot_cost(q, qd, qdd, ee_pos, u, cost_func,final_term, tgrid):
    n_joints = len(q)
    # Setting for the axis
    gridspec_kw={   'wspace': 0.4,
                    'hspace': 0.4}
    
    # Instantiating plot
    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(6,4), gridspec_kw=gridspec_kw)

    # Refactor function for q and its derivatives to be [q0(0), q1(0), q2(0)],[q0(1), q1(1), q2(1)] etc
    ref = lambda q : [np.array([q[j][idx] for j in range(n_joints)]) for idx in range(len(q[0]))]

    # Calculating the value of the cost function for each point
    iterator = zip(ref(q), ref(qd), ref(qdd), ref(ee_pos), ref(u), tgrid)
    cost_plot = np.array([cost_func(q,qd,qdd,ee_pos,u,t) for q,qd,qdd,ee_pos,u,t in iterator])
    cost_plot = np.squeeze(cost_plot)

    # Final Value
    cumulated_cost = [sum(cost_plot[:idx+1]) for idx in range(len(cost_plot))]
    
    if final_term is not None:
        # Storing the variable for the final term cost
        qf = [q[i][-1] for i in range(n_joints)]
        qdf = [qd[i][-1] for i in range(n_joints)]
        qddf = [qdd[i][-1] for i in range(n_joints)]
        ee_posf = [ee_pos[i][-1] for i in range(3)]
        uf = [u[i][-1] for i in range(n_joints)]
        # Evaluating the final term cost
        final_cost = float(final_term(qf,qdf,qddf,ee_posf,uf))
    else:
        final_cost = 0

    # Plotting both final term cost and the cost function
    legend = ['cumulated cost function', 'cost function']
    axes.plot(tgrid[:-1], cumulated_cost, '-', color='tab:orange')
    axes.fill_between(tgrid[:-1], cumulated_cost, color='tab:orange') 
    axes.plot(tgrid[:-1], cost_plot, '-', color='tab:blue')
    axes.fill_between(tgrid[:-1], cost_plot, color='tab:blue')
    if final_term is not None:
        axes.arrow(tgrid[-2], 0, 0, final_cost, head_length=0.1, color='tab:pink', width=0.0005)
        legend.append['final term']
    axes.legend(legend)
    # Displaying the numerical value
    string = f'Cost Func: {cumulated_cost[-1]:.2e} \nFinal Term: {final_cost:.2e}'
    axes.text(0,1.015,string, transform = axes.transAxes)
    # Setting the labels
    axes.set_xlabel('time')
    axes.set_ylabel('cost function')
    return fig

def plot_constraints(q, qd, qdd, ee_pos, u, constraints, tgrid):
    n_constr = len(constraints)
    n_joints = len(q)

    figures = []

    # Refactoring functions
    ref_joint = lambda q : [np.array([q[j][idx] for j in range(n_joints)]) for idx in range(len(q[0]))]
    ref_constr = lambda v : [np.array([array[i] for array in v]) for i in range(lenght)]

    for idx, constraint in enumerate(constraints):
        
        # Calculating the value of the contraints all along the x axis
        iterator = zip(ref_joint(q), ref_joint(qd), ref_joint(qdd), ref_joint(ee_pos), ref_joint(u))
        constr_plot = [constraint(q,qd,qdd,ee_pos,u) for q,qd,qdd,ee_pos,u in iterator]

        # Unpacking value and bounds
        low_bound = np.array([instant[0] for instant in constr_plot])
        value = np.array([instant[1] for instant in constr_plot])
        high_bound = np.array([instant[2] for instant in constr_plot])

        # Creating the plot
        lenght = len(value[0])
        fig, axes = plt.subplots(nrows=1, ncols=lenght, figsize=(9,2))

        iterator = zip(ref_constr(low_bound), ref_constr(value), ref_constr(high_bound), axes)

        # Iterate trough each constraint along the time
        for n, (lb, value, ub, ax) in enumerate(iterator):
            ax.set_facecolor((1.0, 0.45, 0.4))

            # Painting the ok zone in white
            ax.fill_between(tgrid[:-1], lb, ub, color='w')
            ax.plot(tgrid[:-1], low_bound, '-', color='tab:red')
            ax.plot(tgrid[:-1], high_bound, '-', color='tab:red')
            ax.plot(tgrid[:-1], value, '-')
            ax.set_xlim(tgrid[0], tgrid[-2])
            ax.set_xlabel('time')
            ax.set_title('Constraint '+str(idx)+ ' ' +str([n]))

        figures.append(fig)
    return figures
